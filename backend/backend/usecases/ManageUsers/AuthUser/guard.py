from typing import Dict, Any
from fastapi import Request, HTTPException, status, Depends
from pydantic import BaseModel

from usecases.ManageUsers.AuthUser.Controller import decode_access_token


class CurrentUser(BaseModel):
    user_id: str
    claims: Dict[str, Any]

def get_current_user_from_bearer(request: Request) -> CurrentUser:
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")
    token = auth.split(" ", 1)[1].strip()
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    return CurrentUser(user_id=user_id, claims=payload)