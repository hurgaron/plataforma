from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Form, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND
from app.database import SessionLocal
from app.models.usuario import Usuario
from app.auth import ALGORITHM, SECRET_KEY, verificar_senha, criar_token
from sqlalchemy.orm import Session
from fastapi import Cookie
from jose import jwt

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(request: Request, response: Response,
          usulogin: str = Form(...), ususenha: str = Form(...),
          db: Session = Depends(get_db)):

    usuario = db.query(Usuario).filter(Usuario.usuemail == usulogin).first()
    if not usuario or not verificar_senha(ususenha, usuario.ususenha):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "erro": "Login ou senha inválidos"
        })

    exp = datetime.utcnow() + timedelta(minutes=30)
    exp_ts = int(exp.timestamp())
    payload = {"sub": str(usuario.usucod), "exp": exp_ts}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    resp = RedirectResponse(url="/dashboard", status_code=302)
    resp.set_cookie("access_token", token, httponly=True, samesite="lax", secure=False)
    resp.set_cookie("exp_ts", str(exp_ts), httponly=False, samesite="lax")

    return resp