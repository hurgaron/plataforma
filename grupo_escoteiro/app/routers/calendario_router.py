from sqlalchemy.dialects import postgresql
from sqlalchemy import text
import matplotlib.pyplot as plt
import base64
from calendar import monthrange
import io
from typing import List
from fastapi import APIRouter, Query, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session
from datetime import date, datetime
from app.auth import get_db, obter_usuario_logado
from app.models.atividade import Atividade
from app.models.calendario import Calendario
from fastapi.templating import Jinja2Templates
from app.models.atividade_participante import AtividadeParticipante
from app.models.jovem import Jovem
from app.models.adulto import Adulto
from app.models.atividade_custo import AtividadeCusto
from app.models.enums import TipoLancamentoEnum
from app.models.atividade_receita import AtividadeReceita
from app.models.atividade_receita import AtividadeReceita
from app.models.atividade_custo import AtividadeCusto
from fpdf import FPDF
import matplotlib
matplotlib.use("Agg")  # <- Adicione esta linha antes de importar pyplot


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/calendario", response_class=HTMLResponse)
def exibir_calendario(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    calendarios = db.query(Calendario).filter(
        Calendario.empid == usuario.empid).all()

    # Agrupamento simples com base no nome
    grupos = {
        "Ramos": [],
        "Diretoria": [],
    }

    for cal in calendarios:
        grupo = "Diretoria" if "reunião" in cal.calnome.lower() else "Ramos"
        grupos[grupo].append({
            "calid": cal.calid,
            "nome": cal.calnome,
            "cor": cal.cor or "#8B1E3F"
        })

    grupos_de_calendarios = [
        {"nome": nome, "itens": itens} for nome, itens in grupos.items()
    ]

    return templates.TemplateResponse("calendario.html", {
        "request": request,
        "grupos_de_calendarios": grupos_de_calendarios,
        "usuario": usuario,
        "hoje": date.today()
    })


@router.get("/calendario/eventos")
def listar_eventos(
    calids: List[int] = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    query = db.query(Atividade).filter(Atividade.empid == usuario.empid)

    if calids:
        query = query.filter(Atividade.calid.in_(calids))

    print(query.statement.compile(dialect=postgresql.dialect(),
          compile_kwargs={"literal_binds": True}))

    atividades = query.all()
    eventos = [
        {
            "id": a.atid,
            "title": a.titulo,
            "start": a.data_inicio.isoformat(),
            "end": a.data_fim.isoformat(),
            "color": a.calendario.cor if a.calendario else "#8B1E3F",
            "extendedProps": {
                "local": a.local or "",
                "descricao": a.descricao or "",
                "calendario": a.calendario.calnome if a.calendario else ""
            }
        } for a in atividades
    ]
    return JSONResponse(eventos)


@router.get("/calendario/nova", response_class=HTMLResponse)
def nova_atividade(data: str, request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    data_inicio = datetime.fromisoformat(data)
    data_fim = data_inicio.replace(hour=18)
    return templates.TemplateResponse("modal_atividade.html", {
        "request": request,
        "atividade": None,
        "data_inicio": data_inicio,
        "data_fim": data_fim
    })


@router.get("/calendario/{atid}/editar", response_class=HTMLResponse)
def editar_atividade(atid: int, request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    atividade = db.query(Atividade).filter(
        Atividade.atid == atid, Atividade.empid == usuario.empid).first()
    if not atividade:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
    return templates.TemplateResponse("modal_atividade.html", {
        "request": request,
        "atividade": atividade,
        "data_inicio": atividade.data_inicio,
        "data_fim": atividade.data_fim
    })


@router.post("/calendario/salvar")
def salvar_atividade(
    request: Request,
    atid: int = Form(None),
    titulo: str = Form(...),
    descricao: str = Form(None),
    data_inicio: str = Form(...),
    data_fim: str = Form(...),
    local: str = Form(None),
    calid: int = Form(...),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    if atid:
        atividade = db.query(Atividade).filter(
            Atividade.atid == atid, Atividade.empid == usuario.empid).first()
        if not atividade:
            raise HTTPException(
                status_code=404, detail="Atividade não encontrada")
    else:
        atividade = Atividade(empid=usuario.empid, criado_por=usuario.usucod)

    atividade.titulo = titulo
    atividade.descricao = descricao
    atividade.data_inicio = datetime.fromisoformat(data_inicio)
    atividade.data_fim = datetime.fromisoformat(data_fim)
    atividade.local = local
    atividade.calid = calid

    db.add(atividade)
    db.commit()
    db.refresh(atividade)

    return JSONResponse({"sucesso": True, "atid": atividade.atid})


@router.post("/calendario/{atid}/atualizar-data")
def atualizar_data(atid: int, payload: dict, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    atividade = db.query(Atividade).filter(
        Atividade.atid == atid, Atividade.empid == usuario.empid).first()
    if not atividade:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")

    atividade.data_inicio = datetime.fromisoformat(payload["start"])
    atividade.data_fim = datetime.fromisoformat(payload["end"])
    db.commit()
    return {"sucesso": True}


@router.post("/calendario/{atid}/excluir")
def excluir_atividade(atid: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    atividade = db.query(Atividade).filter(
        Atividade.atid == atid, Atividade.empid == usuario.empid).first()
    if not atividade:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
    db.delete(atividade)
    db.commit()
    return {"sucesso": True}


@router.get("/calendario/{atid}/participantes", response_class=HTMLResponse)
def listar_participantes(atid: int, request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    atividade = db.query(Atividade).filter_by(
        atid=atid, empid=usuario.empid).first()
    if not atividade:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")

    lista = []
    for p in atividade.participantes:
        nome = ""
        if p.tipo == "jovem":
            pessoa = db.query(Jovem).filter_by(jovcod=p.pessoa_id).first()
            nome = pessoa.jovnome if pessoa else "(jovem removido)"
        else:
            pessoa = db.query(Adulto).filter_by(aducod=p.pessoa_id).first()
            nome = pessoa.adunome if pessoa else "(adulto removido)"
        lista.append({"id": p.id, "tipo": p.tipo, "nome": nome})

    return templates.TemplateResponse("partials/participantes_lista.html", {"request": request, "participantes": lista})


@router.post("/calendario/{atid}/participantes/adicionar")
def adicionar_participante(atid: int, tipo: str = Form(...), pessoa_id: int = Form(...), db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    atividade = db.query(Atividade).filter_by(
        atid=atid, empid=usuario.empid).first()
    if not atividade:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")

    participante = AtividadeParticipante(
        atid=atid,
        tipo=tipo,
        pessoa_id=pessoa_id,
        empid=usuario.empid
    )
    db.add(participante)
    db.commit()
    return {"sucesso": True}


@router.post("/calendario/participantes/{id}/remover")
def remover_participante(id: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    participante = db.query(AtividadeParticipante).filter_by(
        id=id, empid=usuario.empid).first()
    if not participante:
        raise HTTPException(
            status_code=404, detail="Participante não encontrado")
    db.delete(participante)
    db.commit()
    return {"sucesso": True}


@router.get("/calendario/{atid}/custos", response_class=HTMLResponse)
def listar_custos(atid: int, request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    atividade = db.query(Atividade).filter_by(
        atid=atid, empid=usuario.empid).first()
    if not atividade:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")

    custos = db.query(AtividadeCusto).filter_by(
        atid=atid, empid=usuario.empid).all()
    return templates.TemplateResponse("partials/custos_lista.html", {"request": request, "custos": custos})


@router.post("/calendario/{atid}/custos/adicionar")
def adicionar_custo(
    atid: int,
    descricao: str = Form(...),
    quantidade: float = Form(...),
    valor_unitario: float = Form(...),
    tipo_lancamento: TipoLancamentoEnum = Form(...),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    atividade = db.query(Atividade).filter_by(
        atid=atid, empid=usuario.empid).first()
    if not atividade:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")

    custo = AtividadeCusto(
        atid=atid,
        descricao=descricao,
        quantidade=quantidade,
        valor_unitario=valor_unitario,
        tipo_lancamento=tipo_lancamento,
        empid=usuario.empid
    )
    db.add(custo)
    db.commit()
    return {"sucesso": True}


@router.post("/calendario/custos/{id}/remover")
def remover_custo(id: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    custo = db.query(AtividadeCusto).filter_by(
        id=id, empid=usuario.empid).first()
    if not custo:
        raise HTTPException(status_code=404, detail="Custo não encontrado")
    db.delete(custo)
    db.commit()
    return {"sucesso": True}


@router.get("/calendario/{atid}/receitas", response_class=HTMLResponse)
def listar_receitas(atid: int, request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    atividade = db.query(Atividade).filter_by(
        atid=atid, empid=usuario.empid).first()
    if not atividade:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")

    receitas = db.query(AtividadeReceita).filter_by(
        atid=atid, empid=usuario.empid).all()
    return templates.TemplateResponse("partials/receitas_lista.html", {"request": request, "receitas": receitas})


@router.post("/calendario/{atid}/receitas/adicionar")
def adicionar_receita(
    atid: int,
    descricao: str = Form(...),
    quantidade: float = Form(...),
    valor_unitario: float = Form(...),
    tipo_lancamento: TipoLancamentoEnum = Form(...),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    atividade = db.query(Atividade).filter_by(
        atid=atid, empid=usuario.empid).first()
    if not atividade:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")

    receita = AtividadeReceita(
        atid=atid,
        descricao=descricao,
        quantidade=quantidade,
        valor_unitario=valor_unitario,
        tipo_lancamento=tipo_lancamento,
        empid=usuario.empid
    )
    db.add(receita)
    db.commit()
    return {"sucesso": True}


@router.post("/calendario/receitas/{id}/remover")
def remover_receita(id: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    receita = db.query(AtividadeReceita).filter_by(
        id=id, empid=usuario.empid).first()
    if not receita:
        raise HTTPException(status_code=404, detail="Receita não encontrada")
    db.delete(receita)
    db.commit()
    return {"sucesso": True}


@router.get("/api/jovens/lista")
def listar_jovens(db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    jovens = db.query(Jovem).filter(Jovem.empid == usuario.empid).all()
    return [{"id": j.jovcod, "nome": j.jovnome} for j in jovens]


@router.get("/api/adultos/lista")
def listar_adultos(db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    adultos = db.query(Adulto).filter(Adulto.empid == usuario.empid).all()
    return [{"id": a.aducod, "nome": a.adunome} for a in adultos]


@router.get("/calendario/custos/{id}/editar")
def obter_custo(id: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    custo = db.query(AtividadeCusto).filter_by(
        id=id, empid=usuario.empid).first()
    if not custo:
        raise HTTPException(status_code=404, detail="Custo não encontrado")
    return {
        "id": custo.id,
        "descricao": custo.descricao,
        "quantidade": custo.quantidade,
        "valor_unitario": custo.valor_unitario,
        "tipo_lancamento": custo.tipo_lancamento.value,
        "tipo": custo.tipo
    }


@router.post("/calendario/custos/{id}/atualizar")
def atualizar_custo(
    id: int,
    descricao: str = Form(...),
    quantidade: float = Form(...),
    valor_unitario: float = Form(...),
    tipo_lancamento: TipoLancamentoEnum = Form(...),
    tipo: str = Form(None),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    custo = db.query(AtividadeCusto).filter_by(
        id=id, empid=usuario.empid).first()
    if not custo:
        raise HTTPException(status_code=404, detail="Custo não encontrado")

    custo.descricao = descricao
    custo.quantidade = quantidade
    custo.valor_unitario = valor_unitario
    custo.tipo_lancamento = tipo_lancamento
    custo.tipo = tipo
    db.commit()
    return {"sucesso": True}


@router.get("/atividade/{atid}/balanco", response_class=HTMLResponse)
def balanco_atividade(atid: int, request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    atividade = db.query(Atividade).filter(Atividade.atid == atid).first()
    if not atividade:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

    receitas = db.query(AtividadeReceita).filter(
        AtividadeReceita.atid == atid).all()
    custos = db.query(AtividadeCusto).filter(AtividadeCusto.atid == atid).all()

    def soma(lista, tipo_lancamento):
        return sum(
            r.quantidade * r.valor_unitario
            for r in lista
            if r.tipo_lancamento.value == tipo_lancamento
        )

    total_receita_prev = soma(receitas, "previsto")
    total_receita_real = soma(receitas, "realizado")
    total_custo_prev = soma(custos, "previsto")
    total_custo_real = soma(custos, "realizado")

    saldo_prev = total_receita_prev - total_custo_prev
    saldo_real = total_receita_real - total_custo_real

    return templates.TemplateResponse("atividade_balanco.html", {
        "request": request,
        "atividade": atividade,
        "receitas": receitas,
        "custos": custos,
        "total_receita_prev": total_receita_prev,
        "total_receita_real": total_receita_real,
        "total_custo_prev": total_custo_prev,
        "total_custo_real": total_custo_real,
        "saldo_prev": saldo_prev,
        "saldo_real": saldo_real,
        "usuario": usuario
    })


def gerar_grafico(receita_prev, receita_real, custo_prev, custo_real, saldo_prev, saldo_real):
    labels = [
        "Receita Prevista", "Receita Realizada",
        "Custo Previsto", "Custo Realizado",
        "Saldo Previsto", "Saldo Realizado"
    ]
    values = [receita_prev, receita_real, custo_prev,
              custo_real, saldo_prev, saldo_real]
    colors = ["#d97706", "#8B1E3F", "#e11d48", "#1E40AF", "#047857", "#0f766e"]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, values, color=colors)
    ax.set_title("Comparativo Financeiro da Atividade")
    plt.xticks(rotation=20, ha='right')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", 'B', 14)
        self.set_text_color(139, 30, 63)
        self.cell(0, 10, "Balanço da Atividade", ln=True)
        self.set_draw_color(139, 30, 63)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        from datetime import date
        self.set_y(-15)
        self.set_font("Helvetica", 'I', 8)
        self.set_text_color(128)
        self.cell(
            0, 10, f'Emitido em {date.today().strftime("%d/%m/%Y")} - Página {self.page_no()}', 0, 0, 'C')


@router.get("/atividade/{atid}/balanco/pdf")
def gerar_pdf_atividade(atid: int, db: Session = Depends(get_db)):
    atividade = db.query(Atividade).filter(Atividade.atid == atid).first()
    if not atividade:
        return StreamingResponse(io.BytesIO("Atividade não encontrada".encode("utf-8")), media_type="text/plain", status_code=404)

    receitas = db.query(AtividadeReceita).filter(
        AtividadeReceita.atid == atid).all()
    custos = db.query(AtividadeCusto).filter(AtividadeCusto.atid == atid).all()

    participantes = db.execute(
        text("""
            SELECT j.jovnome AS nome, 'jovem' AS tipo
            FROM atividade_participante ap
            JOIN jovem j ON j.jovcod = ap.pessoa_id
            WHERE ap.tipo = 'jovem' AND ap.atid = :atid
            UNION
            SELECT a.adunome AS nome, 'adulto' AS tipo
            FROM atividade_participante ap
            JOIN adulto a ON a.aducod = ap.pessoa_id
            WHERE ap.tipo = 'adulto' AND ap.atid = :atid
        """), {"atid": atid}
    ).fetchall()

    total_receita_prev = sum(
        r.quantidade * r.valor_unitario for r in receitas if r.tipo_lancamento.value == 'previsto')
    total_receita_real = sum(
        r.quantidade * r.valor_unitario for r in receitas if r.tipo_lancamento.value == 'realizado')
    total_custo_prev = sum(
        c.quantidade * c.valor_unitario for c in custos if c.tipo_lancamento.value == 'previsto')
    total_custo_real = sum(
        c.quantidade * c.valor_unitario for c in custos if c.tipo_lancamento.value == 'realizado')
    saldo_prev = total_receita_prev - total_custo_prev
    saldo_real = total_receita_real - total_custo_real

    grafico = gerar_grafico(total_receita_prev, total_receita_real,
                            total_custo_prev, total_custo_real, saldo_prev, saldo_real)

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", '', 11)
    pdf.set_text_color(0)
    pdf.cell(0, 6, f"Título: {atividade.titulo}", ln=True)
    pdf.cell(0, 6, f"Local: {atividade.local}", ln=True)
    pdf.cell(
        0, 6, f"Data: {atividade.data_inicio.strftime('%d/%m/%Y %H:%M')} até {atividade.data_fim.strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 8, "Participantes", ln=True)
    pdf.set_font("Helvetica", '', 10)
    for p in participantes:
        pdf.cell(0, 6, f"- {p.tipo.capitalize()}: {p.nome}", ln=True)
    pdf.ln(3)

    def tabela(titulo, itens):
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 8, titulo, ln=True)
        pdf.set_font("Helvetica", 'B', 10)
        pdf.set_fill_color(240, 240, 240)
        headers = ["Descrição", "Qtd", "V. Unit.", "Previsto", "Realizado"]
        for h in headers:
            pdf.cell(38 if h == "Descrição" else 30, 8,
                     h, border=1, align='C', fill=True)
        pdf.ln()
        pdf.set_font("Helvetica", '', 10)
        for i in itens:
            prev = f"R$ {i.quantidade * i.valor_unitario:,.2f}" if i.tipo_lancamento.value == 'previsto' else "-"
            real = f"R$ {i.quantidade * i.valor_unitario:,.2f}" if i.tipo_lancamento.value == 'realizado' else "-"
            pdf.cell(38, 8, i.descricao[:25], border=1)
            pdf.cell(30, 8, f"{i.quantidade:.2f}", border=1, align='R')
            pdf.cell(30, 8, f"R$ {i.valor_unitario:,.2f}", border=1, align='R')
            pdf.cell(30, 8, prev, border=1, align='R')
            pdf.cell(30, 8, real, border=1, align='R')
            pdf.ln()
        pdf.ln(2)

    tabela("Receitas", receitas)
    tabela("Custos", custos)

    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 8, "Saldos", ln=True)
    pdf.set_font("Helvetica", '', 11)
    pdf.cell(60, 8, "Saldo Previsto:", 1, 0, 'L')
    pdf.cell(40, 8, f"R$ {saldo_prev:,.2f}", 1, 1, 'R')
    pdf.cell(60, 8, "Saldo Realizado:", 1, 0, 'L')
    pdf.cell(40, 8, f"R$ {saldo_real:,.2f}", 1, 1, 'R')

    # Inserir gráfico como imagem
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "Gráfico Comparativo", ln=True)
    pdf.image(grafico, x=20, w=170)

    output = io.BytesIO()
    pdf.output(output)
    output.seek(0)
    return StreamingResponse(output, media_type="application/pdf", headers={
        "Content-Disposition": f"inline; filename=balanco_atividade_{atid}.pdf"
    })


def gerar_grafico_base64(receita_prev, receita_real, custo_prev, custo_real, saldo_prev, saldo_real):
    labels = [
        "Receita Prevista", "Receita Realizada",
        "Custo Previsto", "Custo Realizado",
        "Saldo Previsto", "Saldo Realizado"
    ]
    values = [receita_prev, receita_real, custo_prev,
              custo_real, saldo_prev, saldo_real]
    colors = ["#d97706", "#8B1E3F", "#e11d48", "#1E40AF", "#047857", "#0f766e"]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, values, color=colors)
    ax.set_title("Comparativo Financeiro da Atividade")
    plt.xticks(rotation=20, ha='right')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    buf.seek(0)

    return f"data:image/png;base64,{base64.b64encode(buf.read()).decode('utf-8')}"


@router.get("/atividade/{atid}/balanco/impressao", response_class=HTMLResponse)
def balanco_atividade_impressao(atid: int, request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    atividade = db.query(Atividade).filter(Atividade.atid == atid).first()
    if not atividade:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")

    receitas = db.query(AtividadeReceita).filter(
        AtividadeReceita.atid == atid).all()
    custos = db.query(AtividadeCusto).filter(AtividadeCusto.atid == atid).all()

    participantes = db.execute(text("""
        SELECT j.jovnome AS nome, 'jovem' AS tipo
        FROM atividade_participante ap
        JOIN jovem j ON j.jovcod = ap.pessoa_id
        WHERE ap.tipo = 'jovem' AND ap.atid = :atid
        UNION
        SELECT a.adunome AS nome, 'adulto' AS tipo
        FROM atividade_participante ap
        JOIN adulto a ON a.aducod = ap.pessoa_id
        WHERE ap.tipo = 'adulto' AND ap.atid = :atid
    """), {"atid": atid}).fetchall()

    def soma(lista, tipo_lancamento):
        return sum(
            r.quantidade * r.valor_unitario
            for r in lista
            if r.tipo_lancamento.value == tipo_lancamento
        )

    total_receita_prev = soma(receitas, "previsto")
    total_receita_real = soma(receitas, "realizado")
    total_custo_prev = soma(custos, "previsto")
    total_custo_real = soma(custos, "realizado")
    saldo_prev = total_receita_prev - total_custo_prev
    saldo_real = total_receita_real - total_custo_real

    # Opcional: gerar imagem base64 do gráfico
    grafico_base64 = gerar_grafico_base64(
        total_receita_prev, total_receita_real,
        total_custo_prev, total_custo_real,
        saldo_prev, saldo_real
    )

    return templates.TemplateResponse("atividade_balanco_impressao.html", {
        "request": request,
        "atividade": atividade,
        "receitas": receitas,
        "custos": custos,
        "participantes": participantes,
        "total_receita_prev": total_receita_prev,
        "total_receita_real": total_receita_real,
        "total_custo_prev": total_custo_prev,
        "total_custo_real": total_custo_real,
        "saldo_prev": saldo_prev,
        "saldo_real": saldo_real,
        "grafico_base64": grafico_base64
    })


@router.get("/calendario/receitas/{id}/editar")
def obter_receita(id: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    receita = db.query(AtividadeReceita).filter_by(
        id=id, empid=usuario.empid).first()
    if not receita:
        raise HTTPException(status_code=404, detail="Receita não encontrada")
    return {
        "id": receita.id,
        "descricao": receita.descricao,
        "quantidade": receita.quantidade,
        "valor_unitario": receita.valor_unitario,
        "tipo_lancamento": receita.tipo_lancamento.value,
        "tipo": receita.tipo
    }


@router.post("/calendario/receitas/{id}/atualizar")
def atualizar_receita(
    id: int,
    descricao: str = Form(...),
    quantidade: float = Form(...),
    valor_unitario: float = Form(...),
    tipo_lancamento: TipoLancamentoEnum = Form(...),
    tipo: str = Form(None),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    receita = db.query(AtividadeReceita).filter_by(
        id=id, empid=usuario.empid).first()
    if not receita:
        raise HTTPException(status_code=404, detail="Receita não encontrada")

    receita.descricao = descricao
    receita.quantidade = quantidade
    receita.valor_unitario = valor_unitario
    receita.tipo_lancamento = tipo_lancamento
    receita.tipo = tipo
    db.commit()
    return {"sucesso": True}


@router.get("/calendario/gerenciar", response_class=HTMLResponse)
def gerenciar_calendarios(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    calendarios = db.query(Calendario).filter(
        Calendario.empid == usuario.empid).all()
    return templates.TemplateResponse("calendarios.html", {
        "request": request,
        "calendarios": calendarios,
        "usuario": usuario
    })


@router.get("/calendario/gerenciar", response_class=HTMLResponse)
def gerenciar_calendarios(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    calendarios = db.query(Calendario).filter(
        Calendario.empid == usuario.empid).all()
    return templates.TemplateResponse("calendarios.html", {
        "request": request,
        "calendarios": calendarios,
        "usuario": usuario
    })


@router.post("/calendario/{calid}/editar")
def editar_calendario(calid: int, calnome: str = Form(...), cor: str = Form(...), db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    cal = db.query(Calendario).filter(Calendario.calid == calid,
                                      Calendario.empid == usuario.empid).first()
    if not cal:
        raise HTTPException(
            status_code=404, detail="Calendário não encontrado")
    cal.calnome = calnome
    cal.cor = cor
    db.commit()
    return RedirectResponse("/calendario/gerenciar", status_code=303)


@router.post("/calendario/{calid}/excluir")
def excluir_calendario(calid: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    cal = db.query(Calendario).filter(Calendario.calid == calid,
                                      Calendario.empid == usuario.empid).first()
    if not cal:
        raise HTTPException(
            status_code=404, detail="Calendário não encontrado")
    if cal.atividades:
        raise HTTPException(
            status_code=400, detail="Calendário possui atividades vinculadas")
    db.delete(cal)
    db.commit()
    return RedirectResponse("/calendario/gerenciar", status_code=303)


@router.post("/calendario")
def criar_calendario(calnome: str = Form(...), cor: str = Form(...), db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    novo = Calendario(calnome=calnome, cor=cor, empid=usuario.empid)
    db.add(novo)
    db.commit()
    return RedirectResponse("/calendario/gerenciar", status_code=303)


@router.get("/calendario/imprimir", response_class=HTMLResponse)
def imprimir_agenda(
    request: Request,
    mes: int,
    ano: int,
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    # Intervalo do mês
    dia_inicio = datetime(ano, mes, 1)
    dia_fim = datetime(ano, mes, monthrange(ano, mes)[1], 23, 59, 59)

    atividades = (
        db.query(Atividade)
        .filter(
            Atividade.empid == usuario.empid,
            Atividade.data_inicio >= dia_inicio,
            Atividade.data_inicio <= dia_fim
        )
        .order_by(Atividade.data_inicio)
        .all()
    )

    return templates.TemplateResponse("agenda_impressao.html", {
        "request": request,
        "atividades": atividades,
        "mes": mes,
        "ano": ano,
        "usuario": usuario
    })


@router.get("/calendario/imprimir/pdf")
def gerar_pdf_agenda(
    mes: int,
    ano: int,
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    from fpdf import FPDF
    from calendar import monthrange

    inicio = datetime(ano, mes, 1)
    fim = datetime(ano, mes, monthrange(ano, mes)[1], 23, 59, 59)

    atividades = (
        db.query(Atividade)
        .filter(
            Atividade.empid == usuario.empid,
            Atividade.data_inicio >= inicio,
            Atividade.data_inicio <= fim
        )
        .order_by(Atividade.data_inicio)
        .all()
    )

    class AgendaPDF(FPDF):
        def header(self):
            self.set_font("Helvetica", 'B', 14)
            self.set_text_color(139, 30, 63)
            self.cell(
                0, 10, f"Agenda de Atividades – {mes:02}/{ano}", ln=True, align='C')
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", 'I', 8)
            self.set_text_color(128)
            self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    pdf = AgendaPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", '', 11)

    if atividades:
        for a in atividades:
            data_str = a.data_inicio.strftime("%d/%m/%Y %H:%M")
            pdf.set_text_color(139, 30, 63)
            pdf.set_font("Helvetica", 'B', 11)
            pdf.cell(0, 8, f"{data_str} – {a.titulo}", ln=True)

            pdf.set_text_color(0)
            pdf.set_font("Helvetica", '', 10)
            pdf.multi_cell(0, 6, f"Local: {a.local or 'Não informado'}")
            if a.descricao:
                pdf.multi_cell(0, 6, f"{a.descricao}")
            pdf.ln(3)
    else:
        pdf.set_font("Helvetica", 'I', 11)
        pdf.cell(0, 10, "Nenhuma atividade cadastrada para este mês.", ln=True)

    output = io.BytesIO()
    pdf.output(output)
    output.seek(0)

    return StreamingResponse(output, media_type="application/pdf", headers={
        "Content-Disposition": f"inline; filename=agenda_{mes:02}_{ano}.pdf"
    })
