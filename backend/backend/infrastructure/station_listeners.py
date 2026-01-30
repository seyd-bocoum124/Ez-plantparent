import json
import logging

from infrastructure.database import Database
from infrastructure.pgpool import obtain_connection_from_pool, \
    release_connection
from usecases.ManageReports.ExpressAnalysis.CreateExpressAnalysisRepport.Handler import handle_express_analysis
from usecases.ManageReports.Watering.CreateWateringReport.Handler import \
    handle_watering_analysis
from usecases.ManageStations.PairStationToUser.Handler import pair_station_to_user
from utils.logging_config import setup_logging
from pydash import get
from typing import Optional

from typing import Callable, Any



# Logging
setup_logging()
logger = logging.getLogger(__name__)

def parse_json_dict(payload_str: str) -> Optional[dict]:
    try:
        parsed = json.loads(payload_str)
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        return None


def station_listener(active_by_station, _main_loop, _safe_task):

    def handle_cmd(client, userdata, msg):
        station_id = extract_station_id(msg)
        payload_str = extract_payload_string(msg)
        
        message: Optional[dict] = parse_json_dict(payload_str)
        if message is None:
            logger.warning("Non-JSON message received: %s", payload_str)
            return

        logger.info("📥 MQTT message: topic=%s type=%s", msg.topic, message.get('type', 'unknown'))

        if is_message_is_compute_express_analysis(message):
            try:
                data = get(message, "data")
                report_id = with_db_connection(
                    lambda db: handle_express_analysis(data, db))

                payload = {
                    "type": "command",
                    "activity": "express_analysis",
                    "action": "present_report",
                    "data": {"report_id": report_id}
                }
                send_message_to_station(
                    station_id,
                    json.dumps(payload, separators=(",", ":"),
                                     ensure_ascii=False))
            except Exception:
                logger.exception("Failed processing message")

        elif is_message_is_compute_watering(message):
            try:
                data = get(message, "data")
                report_id = with_db_connection(
                    lambda db: handle_watering_analysis(data, db))

                # @TODO (PLM) factorise this
                payload = {
                    "type": "command",
                    "activity": "watering",
                    "action": "present_report",
                    "data": {"report_id": report_id}
                }
                send_message_to_station(
                    station_id,
                    json.dumps(payload, separators=(",", ":"),
                                     ensure_ascii=False))
            except Exception:
                logger.exception("Failed processing message")
        elif is_message_is_start_pair_user(message):
            try:
                data = get(message, "data")
                data["station_id"] = station_id

                report_id = with_db_connection(
                    lambda db: pair_station_to_user(data, db))


            except Exception:
                logger.exception("Failed processing message")



        if _main_loop is None:
            logger.warning("Main loop not set, dropping MQTT message")
            return

        text = json.dumps(message)
        if station_id:
            send_message_to_station(station_id, text)
        else:
            for station_id in list(active_by_station.keys()):
                send_message_to_station(station_id, text)

    def is_message_is_compute_express_analysis(message):
        return (get(message, "type") == "command"
                and get(message, "activity") == "express_analysis"
                and get(message, "action") == "compute_report")

    def is_message_is_compute_watering(message):
        return (get(message, "type") == "command"
                and get(message, "activity") == "watering"
                and get(message, "action") == "compute_report")

    def is_message_is_start_pair_user(message):
        return (get(message, "type") == "command"
                and get(message, "activity") == "pair_user"
                and get(message, "action") == "register_code")

    def send_message_to_station(station_id, text):
        async def _notify_station(st_id: str, text_to_send: str):
            for ws in list(active_by_station.get(st_id, set())):
                try:
                    await ws.send_text(text_to_send)
                except Exception:
                    try:
                        active_by_station[st_id].discard(ws)
                    except Exception:
                        pass
                    logger.info("Removed closed websocket for station %s", st_id)
        _main_loop.call_soon_threadsafe(_safe_task,
                                        _notify_station(station_id, text))

    def extract_payload_string(msg):
        try:
            payload = msg.payload.decode()
        except Exception:
            payload = str(msg.payload)
        return payload

    def extract_station_id(msg):
        station_id = None
        parts = msg.topic.split("/")
        if len(parts) >= 2 and parts[0] in ("station", "stations"):
            station_id = parts[1]
        return station_id

    return handle_cmd


def with_db_connection(callback: Callable[[Database], Any]) -> Any:
    conn, from_pool = obtain_connection_from_pool()
    db = Database(conn, commit_on_execute=False)
    try:
        result = callback(db)
        if from_pool:
            try:
                conn.commit()
            except Exception:
                try:
                    conn.rollback()
                except Exception:
                    pass
                raise
        return result
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        release_connection(conn, from_pool)
