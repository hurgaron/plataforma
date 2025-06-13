from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, selectinload
from io import BytesIO
from datetime import date, datetime
import pandas as pd
from fpdf import FPDF

from app.auth import obter_usuario_logado
from app.database import SessionLocal
from app.models.mensalidade import Mensalidade
from app.models.jovem import Jovem
from sqlalchemy import extract

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/relatorios/mensalidades", response_class=HTMLResponse)
def relatorio_mensalidades(
    request: Request,
    mes: int = Query(default=datetime.today().month),
    ano: int = Query(default=datetime.today().year),
    status: str = Query(default="todos"),
    jovcod: int = Query(default=0),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    jovens = db.query(Jovem).filter(Jovem.empid == usuario.empid).all()

    query = db.query(Mensalidade).join(Jovem).filter(Mensalidade.empid == usuario.empid)

    if mes:
        query = query.filter(extract("month", Mensalidade.mendata_venc) == mes)
    if ano:
        query = query.filter(extract("year", Mensalidade.mendata_venc) == ano)
    if status != "todos":
        query = query.filter(Mensalidade.menstatus == status)
    if jovcod != 0:
        query = query.filter(Mensalidade.jovcod == jovcod)

    mensalidades = query.order_by(Mensalidade.mendata_venc).all()

    totais = {
        "pendente": sum(m.menvalor for m in mensalidades if m.menstatus == "pendente"),
        "pago": sum(m.menvalor for m in mensalidades if m.menstatus == "pago"),
        "cancelado": sum(m.menvalor for m in mensalidades if m.menstatus == "cancelado"),
        "total": sum(m.menvalor for m in mensalidades)
    }

    return templates.TemplateResponse("relatorio_mensalidades.html", {
        "request": request,
        "usuario": usuario,
        "jovens": jovens,
        "mensalidades": mensalidades,
        "mes": mes,
        "ano": ano,
        "status": status,
        "jovcod": jovcod,
        "totais": totais
    })

@router.get("/relatorios/mensalidades/pdf")
def baixar_pdf(
    request: Request,
    mes: int = 0,
    ano: int = 0,
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    from sqlalchemy import extract

    query = db.query(Mensalidade).join(Jovem).options(selectinload(Mensalidade.jovem)).filter(Mensalidade.empid == usuario.empid)
    
    if mes and ano:
        query = query.filter(
            extract("month", Mensalidade.mendata_venc) == mes,
            extract("year", Mensalidade.mendata_venc) == ano
        )
    
    mensalidades = query.all()

    # ✅ Transformar em DataFrame
    dados = []
    for m in mensalidades:
        dados.append({
            "Jovem": m.jovem.jovnome if m.jovem else "Desconhecido",
            "Vencimento": m.mendata_venc.strftime('%d/%m/%Y'),
            "Valor": f"R$ {m.menvalor:.2f}",
            "Status": m.menstatus,
            "Observação": m.menobservacao or ""
        })

    df = pd.DataFrame(dados)

    # ✅ Gerar PDF em memória
    buffer = gerar_pdf_em_memoria(df)

    return StreamingResponse(buffer, media_type="application/pdf", headers={
        "Content-Disposition": "attachment; filename=relatorio_mensalidades.pdf"
    })
    
@router.get("/relatorios/mensalidades/excel")
def baixar_excel(
    request: Request,
    mes: int = 0,
    ano: int = 0,
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    from sqlalchemy import extract

    query = db.query(Mensalidade).join(Jovem).options(selectinload(Mensalidade.jovem)).filter(Mensalidade.empid == usuario.empid)

    if mes and ano:
        query = query.filter(
            extract("month", Mensalidade.mendata_venc) == mes,
            extract("year", Mensalidade.mendata_venc) == ano
        )

    mensalidades = query.all()

    # ✅ Montar dados
    dados = []
    for m in mensalidades:
        dados.append({
            "Jovem": m.jovem.jovnome if m.jovem else "Desconhecido",
            "Vencimento": m.mendata_venc.strftime('%d/%m/%Y'),
            "Valor": m.menvalor,
            "Status": m.menstatus,
            "Observação": m.menobservacao or ""
        })

    df = pd.DataFrame(dados)

    # ✅ Gerar Excel em memória
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Mensalidades')
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={
        "Content-Disposition": "attachment; filename=relatorio_mensalidades.xlsx"
    })
    
def gerar_pdf_em_memoria(df: pd.DataFrame):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Relatório de Mensalidades", ln=True, align='C')
    pdf.set_font("Arial", "B", 10)
    for col in df.columns:
        pdf.cell(38, 8, txt=col, border=1)
    pdf.ln()
    pdf.set_font("Arial", size=10)
    for _, row in df.iterrows():
        for item in row:
            texto = str(item)
            if len(texto) > 30:
                texto = texto[:27] + "..."
            pdf.cell(38, 8, txt=texto, border=1)
        pdf.ln()
    buffer = BytesIO()
    buffer.write(pdf.output(dest='S').encode("latin-1"))
    buffer.seek(0)
    return buffer

def gerar_excel_em_memoria(df: pd.DataFrame):
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer

@router.get("/relatorios/mensalidades/excel")
def baixar_excel(
    mes: int = Query(default=datetime.today().month),
    ano: int = Query(default=datetime.today().year),
    status: str = Query(default="todos"),
    jovcod: int = Query(default=0),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    query = db.query(Mensalidade).join(Jovem).filter(Mensalidade.empid == usuario.empid)
    if mes:
        query = query.filter(Mensalidade.mendata_venc.month == mes)
    if ano:
        query = query.filter(Mensalidade.mendata_venc.year == ano)
    if status != "todos":
        query = query.filter(Mensalidade.menstatus == status)
    if jovcod != 0:
        query = query.filter(Mensalidade.jovcod == jovcod)

    dados = query.all()

    df = pd.DataFrame([{
        "Jovem": d.jovem.jovnome,
        "Vencimento": d.mendata_venc.strftime('%d/%m/%Y'),
        "Valor": float(d.menvalor),
        "Status": d.menstatus,
        "Obs": d.menobservacao or ""
    } for d in dados])

    buffer = gerar_excel_em_memoria(df)
    return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={
        "Content-Disposition": "attachment; filename=relatorio_mensalidades.xlsx"
    })

@router.post("/mensalidades/{mensalidade_id}/pagar")
def marcar_como_pago(
    mensalidade_id: int,
    db: Session = Depends(get_db),
    usuario = Depends(obter_usuario_logado)
):
    mensalidade = db.query(Mensalidade).filter(
        Mensalidade.mencod == mensalidade_id,
        Mensalidade.empid == usuario.empid
    ).first()

    if not mensalidade:
        raise HTTPException(status_code=404, detail="Mensalidade não encontrada")

    if mensalidade.menstatus == "pago":
        return {"ok": True, "msg": "Já está paga"}

    mensalidade.menstatus = "pago"
    mensalidade.mendata_pagamento = date.today()
    db.commit()

    return {"ok": True, "msg": "Mensalidade marcada como paga"}