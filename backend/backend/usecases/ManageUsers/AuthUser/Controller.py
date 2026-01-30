import os
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, HTTPException, Response, status, Depends
from jose import jwt, JWTError
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from datetime import datetime, timezone, timedelta

from entities.models import RefreshToken
from entities.repositories import Repository
from infrastructure.database import Database, get_db
import os

logger = logging.getLogger(__name__)
router = APIRouter()



IS_PROD = os.getenv("ENV") == "production"

# Client IDs Google OAuth acceptés (prod + dev)
GOOGLE_CLIENT_IDS = [
    "277969973394-iukhj3ekrkqj7v54e5kria66pc2g435i.apps.googleusercontent.com",  # Prod + Mobile
    "277969973394-aq98febjtlovj8nmktscilj1iknt7cpm.apps.googleusercontent.com",  # Dev
]

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable is required")

JWT_ALGO = os.getenv("JWT_ALGO", "HS256")
ACCESS_TTL = int(os.getenv("ACCESS_TTL", 60 * 30))            # 30 minutes
REFRESH_TTL = int(os.getenv("REFRESH_TTL", 60 * 60 * 24 * 14)) # 14 days


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _to_unix(dt: datetime) -> int:
    return int(dt.timestamp())


def create_access_token(user_id: str, extra_claims: Optional[dict] = None, expires_in: int = ACCESS_TTL) -> str:
    issued_at = _now()
    expires_at = issued_at + timedelta(seconds=expires_in)
    payload = {
        "sub": str(user_id),
        "iat": _to_unix(issued_at),
        "exp": _to_unix(expires_at),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return payload
    except JWTError as e:
        logger.debug("JWT decode error: %s", e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")



@router.post("/auth/google", status_code=200)
async def auth_google(request: Request, response: Response, db: Database = Depends(get_db)):
    repository = Repository(db)
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token manquant")

    token = auth.split(" ", 1)[1].strip()
    
    # Essayer de valider avec chaque Client ID
    idinfo = None
    last_error = None
    for client_id in GOOGLE_CLIENT_IDS:
        try:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), client_id, clock_skew_in_seconds=10)
            logger.info(f"Token validé avec Client ID: {client_id[:20]}...")
            break
        except ValueError as e:
            last_error = e
            continue
    
    if not idinfo:
        logger.error(f"Token invalide pour tous les Client IDs: {last_error}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")

    email = idinfo.get("email")
    sub = idinfo.get("sub")
    if not email or not sub:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Informations utilisateur incomplètes")

    user = repository.get_or_create_user(email=email, google_sub=sub)

    access_token = create_access_token(user_id=str(user.id), extra_claims={"email": user.email})

    expires_at = _now() + timedelta(seconds=REFRESH_TTL)

    rt = RefreshToken(
        id=None,
        user_id=str(user.id),
        email=user.email,
        expires_at=expires_at,
        revoked=False
    )
    refresh_id = repository.create_token(rt)

    cookie_secure = True if IS_PROD else False
    cookie_samesite = None if IS_PROD else "lax"  # en prod : None + Secure=True ; en dev : lax + secure=False

    response.set_cookie(
        key="refresh_id",
        value=str(refresh_id),
        httponly=True,
        secure=cookie_secure,
        samesite=cookie_samesite,
        max_age=REFRESH_TTL,
        path="/"
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email}
    }


@router.post("/auth/refresh", status_code=200)
async def refresh(request: Request, response: Response, db: Database = Depends(get_db)):
    repository = Repository(db)
    refresh_id = request.cookies.get("refresh_id")
    if not refresh_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token manquant")

    rec = repository.get_token_by_id(refresh_id)
    if not rec or rec.expires_at < _now() or rec.revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalide ou expiré")

    user_id = rec.user_id
    email = getattr(rec, "email", None)

    expires_at = _now() + timedelta(seconds=REFRESH_TTL)

    new_token = RefreshToken(
        id=None,
        user_id=user_id,
        email=email,
        expires_at=expires_at,
        revoked=False
    )
    new_refresh_id = repository.rotate_token(old_id=refresh_id, new_token=new_token)

    access_token = create_access_token(user_id=user_id, extra_claims={"email": email} if email else None)

    cookie_secure = True if IS_PROD else False
    cookie_samesite = None if IS_PROD else "lax"  # en prod : None + Secure=True ; en dev : lax + secure=False

    response.set_cookie(
        key="refresh_id",
        value=str(new_refresh_id),
        httponly=True,
        secure=cookie_secure,
        samesite=cookie_samesite,
        max_age=REFRESH_TTL,
        path="/"
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user_id, "email": email}
    }


@router.post("/auth/logout", status_code=200)
async def logout(request: Request, response: Response, db: Database = Depends(get_db)):
    repository = Repository(db)
    refresh_id = request.cookies.get("refresh_id")
    if refresh_id:
        repository.delete_token(refresh_id)
    response.delete_cookie("refresh_id", path="/")
    return {"ok": True}
