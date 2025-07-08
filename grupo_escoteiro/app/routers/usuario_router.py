from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from starlette.status import HTTP_303_SEE_OTHER
from fastapi.templating import Jinja2Templates
from app.database import SessionLocal
from app.auth import obter_usuario_logado, criar_hash_senha, criar_token, criar_cookie_token
from app.models.usuario import Usuario
from app.models.empresa import Empresa


router = APIRouter(prefix="/usuario", tags=["Usuario"])
templates = Jinja2Templates(directory="app/templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_senha(senha: str):
    return pwd_context.hash(senha)

@router.post("/criar_admin")
def criar_usuario_admin(empid: int, usunome: str, usuemail: str, ususenha: str, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.empcod == empid).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")

    existente = db.query(Usuario).filter(Usuario.usuemail == usuemail).first()
    if existente:
        raise HTTPException(status_code=400, detail="Usuário já existe.")

    usuario = Usuario(
        usunome=usunome,
        usuemail=usuemail,
        ususenha=hash_senha(ususenha),
        usufuncao="admin",
        empid=empid
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

@router.get("/usuarios", response_class=HTMLResponse)
def listar_usuarios(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    usuarios = db.query(Usuario).filter(Usuario.empid == usuario.empid).all()
    return templates.TemplateResponse("usuarios/lista.html", {
        "request": request,
        "usuarios": usuarios,
        "usuario": usuario
    })

@router.get("/usuarios/novo", response_class=HTMLResponse)
def novo_usuario_form(request: Request, usuario=Depends(obter_usuario_logado)):
    return templates.TemplateResponse("usuarios/form.html", {"request": request, "usuario":usuario})

@router.post("/usuarios/novo")
def criar_usuario(
    request: Request,
    usunome: str = Form(...),
    usuemail: str = Form(...),
    ususenha: str = Form(...),
    usufuncao: str = Form(...),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    existente = db.query(Usuario).filter(Usuario.usuemail == usuemail).first()
    if existente:
        raise HTTPException(status_code=400, detail="Usuário já existe.")

    novo = Usuario(
        usunome=usunome,
        usuemail=usuemail,
        ususenha=hash_senha(ususenha),
        usufuncao=usufuncao,
        empid=usuario.empid
    )
    db.add(novo)
    db.commit()
    return RedirectResponse(url="/usuario/usuarios", status_code=HTTP_303_SEE_OTHER)

@router.post("/criar")
def criar_empresa(empnome: str, empcnpj: str, db: Session = Depends(get_db)):
    existente = db.query(Empresa).filter(Empresa.empcnpj == empcnpj).first()
    if existente:
        raise HTTPException(status_code=400, detail="Empresa já cadastrada.")
    nova = Empresa(empnome=empnome, empcnpj=empcnpj)
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

@router.get("/editar", response_class=HTMLResponse)
def editar_empresa_form(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    empresa = db.query(Empresa).filter(Empresa.empcod == usuario.empid).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return templates.TemplateResponse("empresa/form.html", {"request": request, "empresa": empresa, "usuario": usuario})

@router.post("/editar")
def editar_empresa(
    empnome: str = Form(...),
    empcnpj: str = Form(...),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    empresa = db.query(Empresa).filter(Empresa.empcod == usuario.empid).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    empresa.empnome = empnome # type: ignore
    empresa.empcnpj = empcnpj # type: ignore
    db.commit()
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)

@router.get("/registrar", response_class=HTMLResponse)
def registrar_form(request: Request):
    return templates.TemplateResponse("registrar.html", {"request": request})

@router.post("/registrar")
def registrar_usuario(
    request: Request,
    nome_empresa: str = Form(...),
    nome_usuario: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db),
):
    # Verifica se já existe usuário com este e-mail
    if db.query(Usuario).filter_by(usuemail=email).first():
        return templates.TemplateResponse("registrar.html", {
            "request": request,
            "erro": "E-mail já cadastrado",
            "nome_empresa": nome_empresa,
            "nome_usuario": nome_usuario,
            "email": email
        })

    # Cria empresa do tipo gratuito
    empresa = Empresa(empnome=nome_empresa, emptipo="gratuito")
    db.add(empresa)
    db.commit()
    db.refresh(empresa)

    # Cria usuário mestre
    novo_usuario = Usuario(
        usunome=nome_usuario,
        usuemail=email,
        ususenha=criar_hash_senha(senha),
        usufuncao="admin",
        empid=empresa.empcod
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    # Autentica e redireciona
    token = criar_token(novo_usuario)
    resposta = RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)
    criar_cookie_token(resposta, token)

    return resposta