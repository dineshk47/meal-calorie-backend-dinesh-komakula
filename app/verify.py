from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2
from pytest import Session

from app.utils.security import decode_access_token
import app.db.crud as crud
from app.db.init_db import get_db


class OAuth2AccessToken(OAuth2):
    def __init__(self, tokenUrl: str = ""):
        super().__init__(tokenUrl=tokenUrl, scheme_name="BearerAccessToken")

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing"
            )
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header"
            )
        return token

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=400, detail={
            "status": "GE40003",
            "error": "Token missing",
        })
    
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail={
                    "status": "GE40102",
                    "error": "Invalid or expired token",
                })
    user_id = int(payload.get("sub"))
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail={
                    "status": "GE40103",
                    "error": "User not found",
                })
    return user