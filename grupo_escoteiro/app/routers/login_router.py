from fastapi import APIRouter, Depends, HTTPException, Request, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.auth import autenticar_usuario, criar_token, criar_cookie_token, get_db
from starlette.status import HTTP_303_SEE_OTHER

router = APIRouter(tags=["Autenticação"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login_usuario(
    request: Request,
    usulogin: str = Form(...),
    ususenha: str = Form(...),
    lembrar: str = Form(None),
    db: Session = Depends(get_db),
):
    usuario = autenticar_usuario(db, usulogin, ususenha)

    if not usuario:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "erro": "Email ou senha inválidos",
            "usulogin": usulogin
        })

    exp_horas = 24 * 30 if lembrar == "on" else 2
    token = criar_token(usuario, exp_horas=exp_horas)

    resposta = RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)
    criar_cookie_token(resposta, token)

    if lembrar == "on":
        resposta.set_cookie("lembrar_email", usulogin, max_age=60*60*24*30)
    else:
        resposta.delete_cookie("lembrar_email")

    return resposta

