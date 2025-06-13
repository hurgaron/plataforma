from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, case

from app.database import SessionLocal
from app.auth import obter_usuario_logado
from app.models.jovem import Jovem
from app.models.adulto import Adulto
from app.models.mensalidade import Mensalidade
from app.models.conta import Conta
from app.models.material import Material
from app.models.movimentacao import Movimentacao
from app.models.atividade import Atividade

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    empid = usuario.empid

    total_jovens = db.query(Jovem).filter(Jovem.empid == empid).count()
    total_adultos = db.query(Adulto).filter(Adulto.empid == empid).count()

    total_mensalidades = db.query(Mensalidade).filter(Mensalidade.empid == empid).count()
    mensalidades_pagas = db.query(Mensalidade).filter(Mensalidade.empid == empid, Mensalidade.menstatus == 'P').count()
    mensalidades_abertas = db.query(Mensalidade).filter(Mensalidade.empid == empid, Mensalidade.menstatus == 'A').count()

    total_a_pagar = db.query(func.coalesce(func.sum(Conta.convalor), 0)).filter(Conta.empid == empid, Conta.constatus == 'P', Conta.contipo == 'P').scalar()
    total_a_receber = db.query(func.coalesce(func.sum(Conta.convalor), 0)).filter(Conta.empid == empid, Conta.constatus == 'P', Conta.contipo == 'R').scalar()

    saldo_caixa = db.query(func.coalesce(func.sum(
        case(
            (Conta.contipo == 'R', Conta.convalor),
            else_=-Conta.convalor
        )
    ), 0)).filter(Conta.empid == empid, Conta.constatus == 'Q').scalar()

    total_materiais = db.query(Material).filter(Material.empid == empid).count()

    proxima_atividade = db.query(Atividade).filter(Atividade.empid == empid).order_by(Atividade.data_inicio.asc()).first()

    proxima_atividade_str = f"{proxima_atividade.titulo} em {proxima_atividade.data_inicio.strftime('%d/%m/%Y')}" if proxima_atividade else None

    info = {
        "total_jovens": total_jovens,
        "total_adultos": total_adultos,
        "total_mensalidades": total_mensalidades,
        "mensalidades_pagas": mensalidades_pagas,
        "mensalidades_abertas": mensalidades_abertas,
        "total_a_pagar": f"{total_a_pagar:,.2f}".replace(",", "."),
        "total_a_receber": f"{total_a_receber:,.2f}".replace(",", "."),
        "saldo_caixa": f"{saldo_caixa:,.2f}".replace(",", "."),
        "total_materiais": total_materiais,
        "proxima_atividade": proxima_atividade_str
    }

    return templates.TemplateResponse("dashboard.html", {"request": request, "info": info, "usuario": usuario})
