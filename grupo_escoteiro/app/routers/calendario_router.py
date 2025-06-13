from calendar import monthrange
from fastapi import APIRouter, Body, Form, HTTPException, Query, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.auth import get_db, obter_usuario_logado
from app.models.calendario import Calendario
from app.models.atividade import Atividade


from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/calendario", response_class=HTMLResponse)
def visualizar_calendario(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    calendarios = db.query(Calendario).filter(Calendario.empid == usuario.empid).all()
    return templates.TemplateResponse("calendario.html", {
        "request": request,
        "calendarios": calendarios,
        "usuario": usuario,
        "hoje": datetime.now()
    })

@router.get("/api/atividades")
def listar_atividades(db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    atividades = db.query(Atividade).filter(Atividade.empid == usuario.empid).all()
    eventos = []
    for a in atividades:
        eventos.append({
            "id": a.atid,
            "title": a.titulo,
            "start": a.data_inicio.isoformat(),
            "end": a.data_fim.isoformat(),
            "backgroundColor": a.calendario.cor or "#2563eb",
            "borderColor": a.calendario.cor or "#2563eb",
            "groupId": a.calid  # necessário para agrupar eventos por calendário
        })
    return JSONResponse(content=eventos)

@router.post("/calendario/atividade/nova")
def criar_atividade(
    titulo: str = Form(...),
    descricao: str = Form(""),
    local: str = Form(""),
    calid: int = Form(...),
    data_inicio: str = Form(...),
    data_fim: str = Form(...),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    atividade = Atividade(
        titulo=titulo,
        descricao=descricao,
        local=local,
        calid=calid,
        data_inicio=datetime.fromisoformat(data_inicio),
        data_fim=datetime.fromisoformat(data_fim),
        criado_por=usuario.usucod,
        empid=usuario.empid
    )
    db.add(atividade)
    db.commit()
    return RedirectResponse("/calendario", status_code=303)

@router.get("/api/atividade/{atid}")
def get_atividade(atid: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    atividade = db.query(Atividade).filter(Atividade.atid == atid, Atividade.empid == usuario.empid).first()
    if not atividade:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")

    return {
        "atid": atividade.atid,
        "titulo": atividade.titulo,
        "descricao": atividade.descricao,
        "data_inicio": atividade.data_inicio.isoformat(),
        "data_fim": atividade.data_fim.isoformat(),
        "local": atividade.local,
        "calid": atividade.calid
    }
    
@router.post("/calendario/atividade/{atid}/editar")
def editar_atividade(
    atid: int,
    titulo: str = Form(...),
    descricao: str = Form(""),
    local: str = Form(""),
    calid: int = Form(...),
    data_inicio: str = Form(...),
    data_fim: str = Form(...),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    atividade = db.query(Atividade).filter(Atividade.atid == atid, Atividade.empid == usuario.empid).first()
    if not atividade:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")

    atividade.titulo = titulo
    atividade.descricao = descricao
    atividade.local = local
    atividade.calid = calid
    atividade.data_inicio = datetime.fromisoformat(data_inicio)
    atividade.data_fim = datetime.fromisoformat(data_fim)
    db.commit()

    return RedirectResponse("/calendario", status_code=303)

@router.post("/calendario/atividade/{atid}/excluir")
def excluir_atividade(
    atid: int,
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    atividade = db.query(Atividade).filter(Atividade.atid == atid, Atividade.empid == usuario.empid).first()
    if not atividade:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
    db.delete(atividade)
    db.commit()
    return JSONResponse(content={"success": True})

@router.post("/calendario/atividade/{atid}/atualizar_data")
def atualizar_data_atividade(
    atid: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    atividade = db.query(Atividade).filter(Atividade.atid == atid, Atividade.empid == usuario.empid).first()
    if not atividade:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")

    try:
        atividade.data_inicio = datetime.fromisoformat(payload["data_inicio"])
        atividade.data_fim = datetime.fromisoformat(payload["data_fim"])
        db.commit()
        return {"success": True}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    
@router.get("/calendario/gerenciar", response_class=HTMLResponse)
def gerenciar_calendarios(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    calendarios = db.query(Calendario).filter(Calendario.empid == usuario.empid).all()
    return templates.TemplateResponse("calendarios.html", {
        "request": request,
        "calendarios": calendarios,
        "usuario": usuario
    })

@router.post("/calendario/gerenciar")
def criar_calendario(
    calnome: str = Form(...),
    cor: str = Form(...),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    novo = Calendario(
        calnome=calnome,
        cor=cor,
        empid=usuario.empid
    )
    db.add(novo)
    db.commit()
    return RedirectResponse("/calendario/gerenciar", status_code=303)

@router.get("/calendario/imprimir", response_class=HTMLResponse)
def imprimir_agenda(
    request: Request,
    ano: int = Query(...),
    mes: int = Query(...),
    calid: int = Query(None),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    calendarios = db.query(Calendario).filter(Calendario.empid == usuario.empid).all()

    # Filtro de data
    data_ini = datetime(ano, mes, 1)
    data_fim = datetime(ano, mes, monthrange(ano, mes)[1], 23, 59, 59)

    query = db.query(Atividade).filter(
        Atividade.empid == usuario.empid,
        Atividade.data_inicio >= data_ini,
        Atividade.data_inicio <= data_fim
    )
    if calid:
        query = query.filter(Atividade.calid == calid)

    atividades = query.order_by(Atividade.data_inicio).all()

    return templates.TemplateResponse("agenda_impressa.html", {
        "request": request,
        "calendarios": calendarios,
        "atividades": atividades,
        "ano": ano,
        "mes": mes,
        "calid": calid,
        "usuario": usuario,
    })
    
@router.post("/calendario/{calid}/excluir")
def excluir_calendario(calid: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    atividades_vinculadas = db.query(Atividade).filter(Atividade.calid == calid, Atividade.empid == usuario.empid).count()
    if atividades_vinculadas > 0:
        raise HTTPException(status_code=400, detail="Não é possível excluir. Este calendário possui atividades vinculadas.")
    
    calendario = db.query(Calendario).filter(Calendario.calid == calid, Calendario.empid == usuario.empid).first()
    if not calendario:
        raise HTTPException(status_code=404, detail="Calendário não encontrado")

    db.delete(calendario)
    db.commit()
    return RedirectResponse("/calendario/gerenciar", status_code=303)


@router.post("/calendario/{calid}/editar")
def editar_calendario(
    calid: int,
    calnome: str = Form(...),
    cor: str = Form(...),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    calendario = db.query(Calendario).filter(Calendario.calid == calid, Calendario.empid == usuario.empid).first()
    if not calendario:
        raise HTTPException(status_code=404, detail="Calendário não encontrado")

    calendario.calnome = calnome
    calendario.cor = cor
    db.commit()
    return RedirectResponse("/calendario/gerenciar", status_code=303)
