from uuid import UUID

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from app.config import config

DB_URL = config.db_url.rstrip("/")
ISSUER = f"{DB_URL}/auth/v1"

jwks_client = PyJWKClient(
    f"{ISSUER}/.well-known/jwks.json"
)

bearer_scheme = HTTPBearer()

# helper func that verifies the token and returns the payload
def verify_token(token: str) -> dict:
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["ES256"],
        audience="authenticated",
        issuer=ISSUER,
        options={"require": ["exp", "iss", "aud", "sub"]},
    )

# get user id from the token and return it as a UUID, for use in the endpoints
def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> UUID:
    try:
        payload = verify_token(credentials.credentials)
        return UUID(payload["sub"])
    except (jwt.PyJWTError, ValueError, KeyError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )