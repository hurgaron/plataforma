from calendar import monthrange
from collections import defaultdict
from datetime import datetime
import json
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from sqlalchemy import extract, func, case

from app.database import SessionLocal
from app.auth import obter_usuario_logado, get_db
from app.models.jovem import Jovem
from app.models.adulto import Adulto
from app.models.mensalidade import Mensalidade
from app.models.conta import Conta
from app.models.material import Material
from app.models.movimentacao import Movimentacao
from app.models.atividade import Atividade

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    empid = usuario.empid

    mes = int(request.query_params.get("mes", datetime.today().month))
    ano = int(request.query_params.get("ano", datetime.today().year))

    # === AGREGADOS ===
    total_jovens = db.query(Jovem).filter(Jovem.empid == empid).count()
    total_adultos = db.query(Adulto).filter(Adulto.empid == empid).count()

    total_mensalidades = db.query(Mensalidade).filter(Mensalidade.empid == empid).count()
    mensalidades_pagas = db.query(Mensalidade).filter(Mensalidade.empid == empid, Mensalidade.menstatus == 'P').count()
    mensalidades_abertas = db.query(Mensalidade).filter(Mensalidade.empid == empid, Mensalidade.menstatus == 'A').count()

    total_a_pagar = db.query(func.coalesce(func.sum(Conta.convalor), 0)).filter(
        Conta.empid == empid, Conta.constatus == 'P', Conta.contipo == 'P').scalar()

    total_a_receber = db.query(func.coalesce(func.sum(Conta.convalor), 0)).filter(
        Conta.empid == empid, Conta.constatus == 'P', Conta.contipo == 'R').scalar()

    saldo_caixa = db.query(func.coalesce(func.sum(
        case(
            (Conta.contipo == 'R', Conta.convalor),
            else_=-Conta.convalor
        )
    ), 0)).filter(Conta.empid == empid, Conta.constatus == 'Q').scalar()

    total_materiais = db.query(Material).filter(Material.empid == empid).count()

    proxima_atividade = db.query(Atividade).filter(
        Atividade.empid == empid
    ).order_by(Atividade.data_inicio.asc()).first()

    proxima_atividade_str = f"{proxima_atividade.titulo} em {proxima_atividade.data_inicio.strftime('%d/%m/%Y')}" if proxima_atividade else None

    # === GRÁFICO DE BARRAS POR DIA ===
    dias_mes = [f"{d:02d}" for d in range(1, monthrange(ano, mes)[1] + 1)]
    contagem_pagamentos = defaultdict(int)
    contagem_abertos = defaultdict(int)

    mensalidades = db.query(Mensalidade).filter(
        Mensalidade.empid == empid,
        extract('month', Mensalidade.mendata_venc) == mes,
        extract('year', Mensalidade.mendata_venc) == ano
    ).all()

    for men in mensalidades:
        dia = men.mendata_venc.strftime('%d')
        if men.menstatus == 'P':
            contagem_pagamentos[dia] += 1
        elif men.menstatus == 'A':
            contagem_abertos[dia] += 1

    dias_labels = dias_mes
    dias_pagos = [contagem_pagamentos[d] for d in dias_mes]
    dias_aberto = [contagem_abertos[d] for d in dias_mes]

    # === CONTEXTO FINAL ===
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "usuario": usuario,
        "pagina_atual": "dashboard",
        "info": {
            "total_jovens": total_jovens,
            "total_adultos": total_adultos,
            "total_mensalidades": total_mensalidades,
            "mensalidades_pagas": mensalidades_pagas,
            "mensalidades_abertas": mensalidades_abertas,
            "total_a_pagar": f"{total_a_pagar:,.2f}".replace(",", "."),
            "total_a_receber": f"{total_a_receber:,.2f}".replace(",", "."),
            "saldo_caixa": f"{saldo_caixa:,.2f}".replace(",", "."),
            "total_materiais": total_materiais,
            "proxima_atividade": proxima_atividade_str,
            "mes": mes,
            "ano": ano,
            "ano_atual": datetime.today().year
        },
        "dias_labels": json.dumps(dias_labels),
        "dias_pagos": json.dumps(dias_pagos),
        "dias_aberto": json.dumps(dias_aberto)
    })
