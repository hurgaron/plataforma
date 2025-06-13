from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import SessionLocal
from app.models.fornecedor import Fornecedor
from app.auth import obter_usuario_logado
from pydantic import BaseModel
from starlette.status import HTTP_302_FOUND

router = APIRouter(prefix="/fornecedores", tags=["Fornecedores"])
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# MODELOS Pydantic para API
class FornecedorCreate(BaseModel):
    fornome: str
    forcnpj: Optional[str] = None
    foremail: Optional[str] = None

class FornecedorOut(BaseModel):
    forcod: int
    fornome: str
    forcnpj: Optional[str]
    foremail: Optional[str]

    class Config:
        orm_mode = True

# ROTAS HTML

@router.get("/", response_class=HTMLResponse)
def listar_fornecedores_html(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    fornecedores = db.query(Fornecedor).filter(Fornecedor.empid == usuario.empid).all()
    return templates.TemplateResponse("fornecedores.html", {
        "request": request,
        "fornecedores": fornecedores,
        "usuario": usuario
    })

@router.get("/novo", response_class=HTMLResponse)
def novo_fornecedor_form(request: Request, usuario=Depends(obter_usuario_logado)):
    return templates.TemplateResponse("fornecedor_form.html", {
        "request": request,
        "usuario": usuario,
        "fornecedor": None
    })

@router.post("/novo")
def salvar_novo_fornecedor(
    request: Request,
    fornome: str = Form(...),
    forcnpj: str = Form(""),
    foremail: str = Form(""),
    db: Session = Depends(get_db),
    usuario = Depends(obter_usuario_logado)
):
    fornecedor = Fornecedor(
        fornome=fornome,
        forcnpj=forcnpj,
        foremail=foremail,
        empid=usuario.empid
    )
    db.add(fornecedor)
    db.commit()
    return RedirectResponse(url="/fornecedores", status_code=302)

@router.get("/{forcod}/editar", response_class=HTMLResponse)
def editar_form_fornecedor(forcod: int, request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    fornecedor = db.query(Fornecedor).filter(Fornecedor.forcod == forcod, Fornecedor.empid == usuario.empid).first()
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    return templates.TemplateResponse("fornecedor_form.html", {
        "request": request,
        "fornecedor": fornecedor,
        "usuario": usuario
    })

@router.post("/{forcod}/editar")
def salvar_edicao_fornecedor(
    forcod: int,
    fornnome: str = Form(...),
    fornobservacao: str = Form(""),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    fornecedor = db.query(Fornecedor).filter(Fornecedor.forcod == forcod, Fornecedor.empid == usuario.empid).first()
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    
    fornecedor.fornnome = fornnome
    fornecedor.fornobservacao = fornobservacao
    db.commit()
    return RedirectResponse(url="/fornecedores", status_code=HTTP_302_FOUND)

@router.post("/{forcod}/excluir")
def excluir_fornecedor(forcod: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    fornecedor = db.query(Fornecedor).filter(Fornecedor.forcod == forcod, Fornecedor.empid == usuario.empid).first()
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    
    db.delete(fornecedor)
    db.commit()
    return RedirectResponse(url="/fornecedores", status_code=HTTP_302_FOUND)

# ROTAS API (REST)

@router.get("/api", response_model=List[FornecedorOut])
def listar_fornecedores_api(db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    return db.query(Fornecedor).filter(Fornecedor.empid == usuario.empid).all()

@router.post("/api", response_model=FornecedorOut)
def criar_fornecedor_api(dados: FornecedorCreate, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    fornecedor = Fornecedor(fornome=dados.fornome, forcnpj=dados.forcnpj, foremail=dados.foremail, empid=usuario.empid)
    db.add(fornecedor)
    db.commit()
    db.refresh(fornecedor)
    return fornecedor

@router.post("/{forcod}/editar")
def atualizar_fornecedor(
    forcod: int,
    fornome: str = Form(...),
    forcnpj: str = Form(""),
    foremail: str = Form(""),
    db: Session = Depends(get_db),
    usuario = Depends(obter_usuario_logado)
):
    fornecedor = db.query(Fornecedor).filter(
        Fornecedor.forcod == forcod,
        Fornecedor.empid == usuario.empid
    ).first()

    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")

    fornecedor.fornome = fornome
    fornecedor.forcnpj = forcnpj
    fornecedor.foremail = foremail
    db.commit()
    return RedirectResponse(url="/fornecedores", status_code=302)
