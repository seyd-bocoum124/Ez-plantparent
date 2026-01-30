import os
import asyncio
import logging
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Set, Optional

from fastapi import FastAPI, Request, APIRouter, WebSocket, WebSocketDisconnect, Depends
from starlette.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket as StarletteWebSocket

from entities.repositories import Repository
from infrastructure.station_listeners import station_listener
from utils.logging_config import setup_logging
from utils.mqtt_client import MQTTClient
from utils.mqtt_wrapper import MQTTWrapper
from utils.routes_auto_import import import_sub_routes
from infrastructure.pgpool import init_pool, close_pool, obtain_connection_from_pool, release_connection
from infrastructure.database import set_db, get_db, Database
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError


# Logging
setup_logging()
logger = logging.getLogger(__name__)

# Registry per station and reference to main asyncio loop
active_by_station: dict[str, Set[StarletteWebSocket]] = defaultdict(set)
_main_loop: Optional[asyncio.AbstractEventLoop] = None

async def _safe_send(ws: StarletteWebSocket, text: str):
    try:
        await ws.send_text(text)
    except Exception:
        # remove closed socket from all station sets
        try:
            for sset in list(active_by_station.values()):
                sset.discard(ws)
        except Exception:
            pass
        logger.info("Removed closed websocket during send")

mqtt_host = os.getenv("MQTT_HOST")
mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
mqtt_raw = None
if mqtt_host and os.environ.get("TESTING") != "1":
    try:
        # Si le port est 8883, utiliser TLS. Sinon, connexion simple.
        if mqtt_port == 8883:
            mqtt_raw = MQTTClient(broker_host=mqtt_host, broker_port=mqtt_port, client_id="backend")
        else:
            mqtt_raw = MQTTClient(broker_host=mqtt_host, broker_port=mqtt_port, client_id="backend", 
                                 ca_cert=None, certfile=None, keyfile=None)
        logger.info(f"MQTT client initialized for {mqtt_host}:{mqtt_port}")
    except Exception as e:
        logger.warning(f"MQTT client initialization failed: {e}. Running without MQTT.")

def _safe_task(coro):
    task = asyncio.create_task(coro)
    def _swallow_done(t):
        try:
            t.result()
        except Exception as e:
            logger.warning("Unhandled exception in background task: %s", e)
    task.add_done_callback(_swallow_done)
    return task

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _main_loop
    # Capture la boucle asyncio qui sert les WebSockets/uvicorn
    _main_loop = asyncio.get_running_loop()

    if os.environ.get("TESTING") != "1":
        dsn = "host={host} port={port} dbname={db} user={user} password={pwd}".format(
            host=os.getenv("DB_HOST", "postgres"),
            port=os.getenv("DB_PORT", "5432"),
            db=os.getenv("DB_NAME", "ezplantparent"),
            user=os.getenv("DB_USER", "postgres"),
            pwd=os.getenv("DB_PASSWORD", "postgres"),
        )
        init_pool(minconn=1, maxconn=10, dsn=dsn)

        if mqtt_raw:
            logger.info("Register mqtt callbacks")
            app.state.mqtt = MQTTWrapper(mqtt_raw, _main_loop, active_by_station)
            mqtt_raw.register_callback("stations/#", station_listener(active_by_station, _main_loop, _safe_task))
        else:
            logger.info("Running without MQTT broker")
            app.state.mqtt = None

    try:
        yield
    finally:
        if os.environ.get("TESTING") != "1":
            try:
                close_pool()
            except Exception:
                pass

# CORS middleware
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["https://localhost:4200", "https://localhost"],  # Ajout de https://localhost pour Capacitor
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

# FastAPI app
app = FastAPI(
    title="EzPlant Parent API",
    version="0.1.0",
    description="API pour la maintenance des plantes",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    debug=True,
    lifespan=lifespan,
    middleware=middleware
)

# @TODO (PLM) seulement dans en dev...
coverage_dir = "backend/usecases/SeeTestsResults"

os.makedirs(coverage_dir, exist_ok=True)

if os.environ.get("TESTING") != "1":
    app.mount("/coverage", StaticFiles(directory=coverage_dir, html=True), name="coverage")

JWT_ALGO = os.getenv("JWT_ALGO", "HS256")
# @TODO (PLM) no majick string, make credentials safe
JWT_SECRET = os.getenv(
    "JWT_SECRET",
    "457502380663-buk1em1ig80chk41qeqjda9iphsrbt37.apps.googleusercontent.com"
)


@app.websocket("/ws/stations/{station_id}")
async def websocket_endpoint(websocket: WebSocket, station_id: str):
    # Accept connection first, then validate
    await websocket.accept()
    
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4003, reason="Missing token")
        return

    # Obtain DB connection manually for WebSocket (middleware doesn't run for WS)
    try:
        try:
            conn, from_pool = obtain_connection_from_pool()
        except RuntimeError:
            current_db = get_db()
            if current_db is None:
                await websocket.close(code=5000, reason="Database unavailable")
                return
            conn = current_db.conn
            from_pool = False
        
        db = Database(conn, commit_on_execute=False)

        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        user_id = int(payload.get("sub"))
        repository = Repository(db)
        station = repository.get_station_by_mac_address(station_id)
        logger.info(f"Authentified WS user {user_id} for station {station_id}")
        if not station or station.user_id != user_id:
            logger.info(f"WS rejected: station={station}, station.user_id={station.user_id if station else None}, user_id={user_id}")
            await websocket.close(code=4003, reason="Unauthorized station access")
            release_connection(conn, from_pool)
            return

        active_by_station.setdefault(station_id, set()).add(websocket)
        logger.info("✅ WebSocket client %s connecté pour station %s (total WS pour cette station: %d)", user_id, station_id, len(active_by_station[station_id]))
    except ExpiredSignatureError:
        await websocket.close(code=4001, reason="Token expired")
        release_connection(conn, from_pool)
        return
    except JWTError:
        await websocket.close(code=4002)
        release_connection(conn, from_pool)
        return
    except Exception:
        release_connection(conn, from_pool)
        raise

    try:
        while True:
            data = await websocket.receive_text()
            text = f"Broadcast: {data}"
            for ws in list(active_by_station.get(station_id, set())):
                _safe_task(_safe_send(ws, text))
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected for station %s", station_id)
    finally:
        active_by_station[station_id].discard(websocket)
        if not active_by_station[station_id]:
            del active_by_station[station_id]
        release_connection(conn, from_pool)



# DB session middleware
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    # 1) try to obtain a connection from the pool; if pool not ready, fallback to get_db()
    try:
        conn, from_pool = obtain_connection_from_pool()
    except RuntimeError:
        current_db = get_db()
        if current_db is None:
            raise RuntimeError("No DB pool and no test DB available; init_pool(...) must be called before handling requests.")
        conn = current_db.conn
        from_pool = False

    # 2) ensure a Database wrapper is installed in the current context if needed
    current_db = get_db()
    created_db = False
    if current_db is None or getattr(current_db, "conn", None) is not conn:
        db = Database(conn, commit_on_execute=False)
        set_db(db)
        created_db = True
    else:
        db = current_db

    # 3) run the request and manage transaction (commit on success only for pool connections)
    try:
        response = await call_next(request)
        try:
            if from_pool:
                conn.commit()
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            raise
        return response
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        # 4) cleanup: unset context DB only if we set it here, then release connection appropriately
        if created_db:
            set_db(None)
        release_connection(conn, from_pool)

# API router import/include
api_router = APIRouter(prefix="/api")
import_sub_routes(api_router)
app.include_router(api_router)

# Healthcheck
@app.get("/health")
def health():
    return {"status": "ok"}
