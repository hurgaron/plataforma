from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from pydantic import BaseModel

from app.database import SessionLocal
from app.auth import obter_usuario_logado
from app.models.adulto import Adulto
from app.models.usuario import Usuario
from app.models.empresa import Empresa

from fastapi import Cookie
from passlib.context import CryptContext

router = APIRouter()
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


# Pydantic para API
class AdultoOut(BaseModel):
    aducod: int
    adunome: str
    adudata_nasc: date

    class Config:
        orm_mode = True

class AdultoCreate(BaseModel):
    adunome: str
    adudata_nasc: date

# Listagem visual
@router.get("/adultos", response_class=HTMLResponse)
def listar_adultos_html(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    adultos = db.query(Adulto).filter(Adulto.empid == usuario.empid).order_by(Adulto.adunome).all()
    return templates.TemplateResponse("adultos.html", {"request": request, "adultos": adultos, "usuario": usuario})

# Formulário novo
@router.get("/adultos/novo", response_class=HTMLResponse)
def novo_adulto_form(request: Request, usuario=Depends(obter_usuario_logado)):
    return templates.TemplateResponse("adultos_novo.html", {"request": request, "usuario": usuario})

@router.post("/adultos/novo")
def salvar_adulto_form(adunome: str = Form(...), adudata_nasc: date = Form(...),
                       db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    novo = Adulto(adunome=adunome, adudata_nasc=adudata_nasc, empid=usuario.empid)
    db.add(novo)
    db.commit()
    return RedirectResponse(url="/adultos", status_code=HTTP_302_FOUND)

# Edição visual
@router.get("/adultos/{aducod}/editar", response_class=HTMLResponse)
def editar_adulto_form(aducod: int, request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    adulto = db.query(Adulto).filter(Adulto.aducod == aducod, Adulto.empid == usuario.empid).first()
    if not adulto:
        raise HTTPException(status_code=404, detail="Adulto não encontrado")
    return templates.TemplateResponse("adultos_editar.html", {"request": request, "adulto": adulto, "usuario": usuario})

@router.post("/adultos/{aducod}/editar")
def salvar_edicao_adulto(aducod: int, adunome: str = Form(...), adudata_nasc: date = Form(...),
                         db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    adulto = db.query(Adulto).filter(Adulto.aducod == aducod, Adulto.empid == usuario.empid).first()
    if not adulto:
        raise HTTPException(status_code=404, detail="Adulto não encontrado")
    adulto.adunome = adunome
    adulto.adudata_nasc = adudata_nasc
    db.commit()
    return RedirectResponse(url="/adultos", status_code=HTTP_302_FOUND)

# Exclusão visual
@router.post("/adultos/{aducod}/excluir")
def excluir_adulto(aducod: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    adulto = db.query(Adulto).filter(Adulto.aducod == aducod, Adulto.empid == usuario.empid).first()
    if not adulto:
        raise HTTPException(status_code=404, detail="Adulto não encontrado")
    db.delete(adulto)
    db.commit()
    return RedirectResponse(url="/adultos", status_code=HTTP_302_FOUND)

# API endpoints
@router.get("/api/adultos", response_model=List[AdultoOut])
def listar_adultos_api(db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    return db.query(Adulto).filter(Adulto.empid == usuario.empid).order_by(Adulto.adunome).all()

@router.post("/api/adultos", response_model=AdultoOut)
def criar_adulto_api(dados: AdultoCreate, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    novo = Adulto(**dados.dict(), empid=usuario.empid)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@router.get("/registrar", response_class=HTMLResponse)
def registrar_form(request: Request):
    return templates.TemplateResponse("auth/registrar.html", {"request": request})

@router.post("/registrar", response_class=HTMLResponse)
def registrar_usuario(
    request: Request,
    usunome: str = Form(...),
    usuemail: str = Form(...),
    ususenha: str = Form(...),
    empcnpj: str = Form(...),
    db: Session = Depends(get_db)
):
    empresa = db.query(Empresa).filter(Empresa.empcnpj == empcnpj).first()
    if not empresa:
        return templates.TemplateResponse("auth/registrar.html", {"request": request, "erro": "Empresa não encontrada. Solicite acesso ao administrador."})

    existente = db.query(Usuario).filter(Usuario.usuemail == usuemail).first()
    if existente:
        return templates.TemplateResponse("auth/registrar.html", {"request": request, "erro": "E-mail já cadastrado."})

    novo = Usuario(
        usunome=usunome,
        usuemail=usuemail,
        ususenha=hash_senha(ususenha),
        usufuncao="colaborador",
        empid=empresa.empcod
    )
    db.add(novo)
    db.commit()

    return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
