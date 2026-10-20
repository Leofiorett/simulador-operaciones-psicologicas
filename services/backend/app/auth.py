import base64
import hashlib
import hmac
import json
import secrets
import time

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import config
from .db import get_db
from .models import User


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(),
        config.PBKDF2_ITERATIONS).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split("$", 1)
    except ValueError:
        return False
    candidate = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(),
        config.PBKDF2_ITERATIONS).hex()
    return hmac.compare_digest(candidate, digest)


def _sign(payload_bytes: bytes) -> str:
    return hmac.new(config.SECRET_KEY.encode(), payload_bytes,
                    hashlib.sha256).hexdigest()


def create_token(username: str, role: str) -> str:
    payload = json.dumps({
        "u": username, "r": role,
        "exp": time.time() + config.TOKEN_TTL_HOURS * 3600,
    }).encode()
    b64 = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    return f"{b64}.{_sign(payload)}"


def decode_token(token: str) -> dict:
    try:
        b64, sig = token.rsplit(".", 1)
        payload = base64.urlsafe_b64decode(b64 + "=" * (-len(b64) % 4))
        if not hmac.compare_digest(_sign(payload), sig):
            raise ValueError("firma invalida")
        data = json.loads(payload)
        if data.get("exp", 0) < time.time():
            raise ValueError("token expirado")
        return data
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Token inválido") from exc


async def get_current_user(request: Request,
                           db: AsyncSession = Depends(get_db)) -> User:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Autenticación requerida")
    data = decode_token(header.removeprefix("Bearer ").strip())
    result = await db.execute(select(User).where(User.username == data["u"]))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="Usuario inexistente")
    return user


async def require_instructor(user: User = Depends(get_current_user)) -> User:
    if user.role != "instructor":
        raise HTTPException(status_code=403,
                            detail="Requiere rol instructor")
    return user
