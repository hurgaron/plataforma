from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date
from app.database import SessionLocal
from app.auth import obter_usuario_logado
from app.models.conta import Conta

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/fluxo-caixa")
def fluxo_caixa(
    request: Request,
    inicio: date = None,
    fim: date = None,
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    if not inicio or not fim:
        hoje = date.today()
        inicio = date(hoje.year, hoje.month, 1)
        fim = date(hoje.year, hoje.month, 28)

    contas = db.query(Conta).filter(
        Conta.empid == usuario.empid,
        Conta.contdata >= inicio,
        Conta.contdata <= fim
    ).order_by(Conta.contdata).all()

    entradas = sum(c.convalor for c in contas if c.contipo == "entrada")
    saidas = sum(c.convalor for c in contas if c.contipo == "saida")
    saldo = entradas - saidas

    return templates.TemplateResponse("fluxo_caixa.html", {
        "request": request,
        "contas": contas,
        "inicio": inicio,
        "fim": fim,
        "entradas": entradas,
        "saidas": saidas,
        "saldo": saldo,
        "usuario": usuario
    })
