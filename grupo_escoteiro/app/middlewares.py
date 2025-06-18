# app/middlewares.py
from fastapi import Request
from fastapi.responses import RedirectResponse
from jose import jwt, JWTError
from datetime import datetime, timezone
from app.auth import SECRET_KEY, ALGORITHM, get_db
from app.models import Usuario
from app.database import SessionLocal

async def token_middleware(request: Request, call_next):
    # rotas públicas não exigem token
    if request.url.path.startswith(("/auth", "/static", "/login", "/docs", "/openapi.json")):
        return await call_next(request)

    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/login", status_code=307)

    # ─── decodifica JWT ────────────────────────────────────────────
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_ts = int(payload["exp"])
        if exp_ts <= int(datetime.now(tz=timezone.utc).timestamp()):
            raise JWTError()
        usucod = int(payload["sub"])
    except (KeyError, JWTError, ValueError):
        return RedirectResponse("/login", status_code=307)

    # ─── carrega usuário (sessão manual, não async) ────────────────
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).get(usucod)
    finally:
        db.close()

    if not usuario:
        return RedirectResponse("/login", status_code=307)

    # grava em request.state para uso posterior / templates
    request.state.usuario = usuario
    request.state.exp_ts  = exp_ts

    return await call_next(request)