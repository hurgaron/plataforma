from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND
from datetime import date
from app.database import SessionLocal
from app.models.conta import Conta
from app.models.fornecedor import Fornecedor
from app.auth import get_db,obter_usuario_logado

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/contas", response_class=HTMLResponse)
def listar_contas(request: Request,
                  tipo: str = "", status: str = "",
                  db: Session = Depends(get_db),
                  usuario = Depends(obter_usuario_logado)):
    query = db.query(Conta).filter(Conta.empid == usuario.empid)

    if tipo:
        query = query.filter(Conta.contipo == tipo)
    if status:
        query = query.filter(Conta.constatus == status)

    contas = query.order_by(Conta.convidovenc).all()
    return templates.TemplateResponse("contas.html", {
        "request": request,
        "contas": contas,
        "tipo": tipo,
        "status": status,
        "usuario": usuario
    })

@router.get("/contas/novo", response_class=HTMLResponse)
def nova_conta_form(request: Request,
                    db: Session = Depends(get_db),
                    usuario = Depends(obter_usuario_logado)):
    fornecedores = db.query(Fornecedor).filter(Fornecedor.empid == usuario.empid).all()
    return templates.TemplateResponse("conta_form.html", {
        "request": request,
        "fornecedores": fornecedores,
        "usuario": usuario
    })

@router.post("/contas/novo")
def criar_conta(
    contipo: str = Form(...),
    condescricao: str = Form(...),
    convalor: float = Form(...),
    convidovenc: date = Form(...),
    constatus: str = Form("pendente"),
    conobservacao: str = Form(""),
    fornecedor_id: int = Form(None),
    db: Session = Depends(get_db),
    usuario = Depends(obter_usuario_logado)
):
    nova = Conta(
        empid=usuario.empid,
        contipo=contipo,
        condescricao=condescricao,
        convalor=convalor,
        convidovenc=convidovenc,
        constatus=constatus,
        conobservacao=conobservacao,
        fornecedor_id=fornecedor_id
    )
    db.add(nova)
    db.commit()
    return RedirectResponse(url="/contas", status_code=HTTP_302_FOUND)

@router.post("/contas/{concod}/pagar")
def pagar_conta(concod: int,
                db: Session = Depends(get_db),
                usuario = Depends(obter_usuario_logado)):
    conta = db.query(Conta).filter(Conta.concod == concod, Conta.empid == usuario.empid).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")

    conta.constatus = "pago"
    db.commit()
    return RedirectResponse(url="/contas", status_code=HTTP_302_FOUND)

@router.get("/contas/{concod}/editar", response_class=HTMLResponse)
def editar_conta_form(concod: int, request: Request, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    conta = db.query(Conta).filter(Conta.concod == concod, Conta.empid == usuario.empid).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    fornecedores = db.query(Fornecedor).filter(Fornecedor.empid == usuario.empid).all()
    return templates.TemplateResponse("conta_form.html", {
        "request": request,
        "conta": conta,
        "fornecedores": fornecedores,
        "usuario": usuario
    })

@router.post("/contas/{concod}/editar")
def salvar_edicao_conta(
    concod: int,
    contipo: str = Form(...),
    condescricao: str = Form(...),
    convalor: float = Form(...),
    convidovenc: date = Form(...),
    constatus: str = Form(...),
    conobservacao: str = Form(""),
    fornecedor_id: str = Form(""),
    db: Session = Depends(get_db),
    usuario = Depends(obter_usuario_logado)
):
    conta = db.query(Conta).filter(Conta.concod == concod, Conta.empid == usuario.empid).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")

    conta.contipo = contipo
    conta.condescricao = condescricao
    conta.convalor = convalor
    conta.convidovenc = convidovenc
    conta.constatus = constatus
    conta.conobservacao = conobservacao
    conta.fornecedor_id = int(fornecedor_id) if fornecedor_id else None

    db.commit()
    return RedirectResponse(url="/contas", status_code=HTTP_302_FOUND)

@router.post("/contas/{concod}/excluir")
def excluir_conta(concod: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    conta = db.query(Conta).filter(Conta.concod == concod, Conta.empid == usuario.empid).first()
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")

    db.delete(conta)
    db.commit()
    return RedirectResponse(url="/contas", status_code=HTTP_302_FOUND)
