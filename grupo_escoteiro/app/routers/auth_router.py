from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND
from app.database import SessionLocal
from app.models.usuario import Usuario
from app.auth import verificar_senha, criar_token
from sqlalchemy.orm import Session
from fastapi import Cookie

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
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.usuemail == username).first()
    if not usuario or not verificar_senha(password, usuario.ususenha):
        return templates.TemplateResponse("login.html", {"request": request, "erro": "Credenciais inválidas"})

    response = RedirectResponse(url="/dashboard", status_code=HTTP_302_FOUND)
    token = criar_token({"sub": str(usuario.usucod)})
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response
