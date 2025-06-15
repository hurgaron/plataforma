from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.auth import get_db, obter_usuario_logado
from app.models import CertificadoNumeracao


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/numeracoes", response_class=HTMLResponse)
def listar_numeracoes(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    numeracoes = db.query(CertificadoNumeracao).filter(CertificadoNumeracao.empid == usuario.empid).all()
    return templates.TemplateResponse("numeracoes.html", {"request": request, "numeracoes": numeracoes, "usuario": usuario})

@router.get("/numeracoes/novo", response_class=HTMLResponse)
def nova_numeracao(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    return templates.TemplateResponse("numeracao_form.html", {"request": request, "usuario": usuario})

@router.post("/numeracoes/novo")
def salvar_numeracao(
    prefixo: str = Form(...),
    descricao: str = Form(None),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    numeracao = CertificadoNumeracao(
        prefixo=prefixo.upper(),
        descricao=descricao,
        empid=usuario.empid
    )
    db.add(numeracao)
    db.commit()
    return RedirectResponse("/numeracoes", status_code=303)

@router.get("/numeracoes/{numid}/editar", response_class=HTMLResponse)
def editar_numeracao(numid: int, request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    numeracao = db.query(CertificadoNumeracao).filter(CertificadoNumeracao.numid == numid, CertificadoNumeracao.empid == usuario.empid).first()
    return templates.TemplateResponse("numeracao_form.html", {"request": request, "numeracao": numeracao, "usuario": usuario})

@router.post("/numeracoes/{numid}/editar")
def salvar_edicao_numeracao(
    numid: int,
    prefixo: str = Form(...),
    descricao: str = Form(None),
    sequencia_atual: int = Form(...),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    numeracao = db.query(CertificadoNumeracao).filter(CertificadoNumeracao.numid == numid, CertificadoNumeracao.empid == usuario.empid).first()
    if numeracao:
        numeracao.prefixo = prefixo.upper()
        numeracao.descricao = descricao
        numeracao.sequencia_atual = sequencia_atual
        db.commit()
    return RedirectResponse("/numeracoes", status_code=303)