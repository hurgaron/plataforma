from datetime import date, datetime
from fastapi import APIRouter, HTTPException, Request, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.models.atividade import Atividade
from app.models.atividade_participante import AtividadeParticipante
from app.auth import get_db, obter_usuario_logado
from fastapi.templating import Jinja2Templates
from typing import Optional
from app.models.jovem import Jovem
from app.models.adulto import Adulto

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/atividade/admin", response_class=HTMLResponse)
def listar_atividades(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    atividades = db.query(Atividade).filter(Atividade.empid == usuario.empid, Atividade.administrativa == True).all()
    return templates.TemplateResponse("atividade/admin_list.html", {"request": request, "atividades": atividades, "usuario": usuario})

@router.get("/atividade/admin/nova", response_class=HTMLResponse)
def nova_atividade(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    return templates.TemplateResponse("atividade/admin_form.html", {"request": request, "atividade": None, "usuario": usuario})

@router.post("/atividade/admin/salvar")
def salvar_atividade(
    titulo: str = Form(...),
    descricao: str = Form(""),
    data_inicio: Optional[datetime] = Form(None),
    data_fim: Optional[datetime] = Form(None),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado),
):
    atividade = Atividade(
        titulo=titulo,
        descricao=descricao,
        data_inicio=data_inicio,
        data_fim=data_fim,
        empid=usuario.empid,
        administrativa=True,
        exibir_no_calendario=False,
        calid=None  # ← sem calendário
    )
    db.add(atividade)
    db.commit()
    return RedirectResponse("/atividade/admin", status_code=303)

@router.get("/atividade/admin/{atid}/editar", response_class=HTMLResponse)
def editar_atividade(
    atid: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario = Depends(obter_usuario_logado)
):
    atividade = db.query(Atividade).filter_by(atid=atid, empid=usuario.empid).first()
    if not atividade:
        return HTMLResponse("Atividade não encontrada", status_code=404)

    participantes_raw = db.query(AtividadeParticipante).filter_by(atid=atid).all()
    participantes = []
    ultimo_valor = ""

    for p in participantes_raw:
        if p.tipo == "jovem":
            pessoa = db.query(Jovem).filter_by(jovcod=p.pessoa_id).first()
            nome = pessoa.jovnome if pessoa else "(jovem removido)"
        else:
            pessoa = db.query(Adulto).filter_by(aducod=p.pessoa_id).first()
            nome = pessoa.adunome if pessoa else "(adulto removido)"

        participantes.append({
            "id": p.id,
            "tipo": p.tipo,
            "nome": nome,
            "valor_pago": p.valor_pago if hasattr(p, "valor_pago") else None,
            "observacao": p.observacao or "",
            "status_pagamento": p.status_pagamento if hasattr(p, "status_pagamento") else "pendente"
        })

    if participantes:
        ultimo = participantes[-1]
        ultimo_valor = f"{ultimo['id']} - {ultimo['nome']}"

    jovens = db.query(Jovem).filter_by(empid=usuario.empid).order_by(Jovem.jovnome).all()
    adultos = db.query(Adulto).filter_by(empid=usuario.empid).order_by(Adulto.adunome).all()

    mensagem_erro = request.session.pop("mensagem_erro", None)
    mensagem_sucesso = request.session.pop("mensagem_sucesso", None)

    return templates.TemplateResponse("atividade/admin_form.html", {
        "request": request,
        "atividade": atividade,
        "participantes": participantes,
        "jovens": jovens,
        "adultos": adultos,
        "usuario": usuario,
        "ultimo_valor": ultimo_valor,
        "mensagem_erro": mensagem_erro,
        "mensagem_sucesso": mensagem_sucesso,
    })



@router.post("/atividade/admin/{atid}/salvar")
def atualizar_atividade(
    atid: int,
    titulo: str = Form(...),
    descricao: str = Form(""),
    data_inicio: date = Form(None),
    data_fim: date = Form(None),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado),
):
    atividade = db.query(Atividade).filter(Atividade.atid == atid, Atividade.empid == usuario.empid).first()
    if not atividade:
        return HTMLResponse("Atividade não encontrada", status_code=404)

    atividade.titulo = titulo
    atividade.descricao = descricao
    atividade.data_inicio = data_inicio
    atividade.data_fim = data_fim
    db.commit()
    return RedirectResponse("/atividade/admin", status_code=303)

@router.post("/atividade/admin/{atid}/excluir")
def excluir_atividade(atid: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    atividade = db.query(Atividade).filter(Atividade.atid == atid, Atividade.empid == usuario.empid).first()
    if not atividade:
        return JSONResponse({"erro": "Atividade não encontrada"}, status_code=404)
    db.delete(atividade)
    db.commit()
    return RedirectResponse("/atividade/admin", status_code=303)

@router.get("/atividade/admin/{atid}/participantes", response_class=HTMLResponse)
def participantes_atividade(atid: int, request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    atividade = db.query(Atividade).filter(Atividade.atid == atid, Atividade.empid == usuario.empid).first()
    if not atividade:
        return HTMLResponse("Atividade não encontrada", status_code=404)
    
    participantes = db.query(AtividadeParticipante).filter_by(atid=atid).all()
    jovens = db.query(Jovem).filter(Jovem.empid == usuario.empid).order_by(Jovem.jovnome).all()

    return templates.TemplateResponse("atividade/admin_participantes.html", {
        "request": request,
        "atividade": atividade,
        "participantes": participantes,
        "jovens": jovens
    })

@router.post("/atividade/admin/{atid}/participantes/adicionar")
def adicionar_participante(
    atid: int,
    request: Request,  
    participante_id: int = Form(...),
    participante_tipo: str = Form(...),
    db: Session = Depends(get_db),
    usuario = Depends(obter_usuario_logado)
):
    existente = db.query(AtividadeParticipante).filter_by(
        atid=atid,
        tipo=participante_tipo,
        pessoa_id=participante_id
    ).first()

    if existente:
        request.session["mensagem_erro"] = "Este participante já está na atividade."
        return RedirectResponse(f"/atividade/admin/{atid}/editar", status_code=303)

    novo = AtividadeParticipante(
        atid=atid,
        tipo=participante_tipo,
        pessoa_id=participante_id,
        empid=usuario.empid,
        status_pagamento="pendente"
    )

    db.add(novo)
    db.commit()

    request.session["mensagem_sucesso"] = "Participante adicionado com sucesso."
    return RedirectResponse(f"/atividade/admin/{atid}/editar", status_code=303)




@router.post("/atividade/admin/{atid}/participantes/{pid}/atualizar")
def atualizar_participante(
    atid: int,
    pid: int,
    status_pagamento: str = Form(...),
    valor_pago: float = Form(...),
    observacao: str = Form(""),
    db: Session = Depends(get_db),
    usuario = Depends(obter_usuario_logado)
):
    p = db.query(AtividadeParticipante).filter_by(atid=atid, id=pid).first()
    if not p:
        raise HTTPException(status_code=404, detail="Participante não encontrado")

    p.status_pagamento = status_pagamento
    p.valor_pago = valor_pago
    p.observacao = observacao

    db.commit()
    return RedirectResponse(f"/atividade/admin/{atid}/editar", status_code=303)

@router.post("/atividade/admin/{atid}/participantes/{pid}/remover")
def remover_participante(
    atid: int,
    pid: int,
    db: Session = Depends(get_db),
    usuario = Depends(obter_usuario_logado)
):
    participante = db.query(AtividadeParticipante).filter_by(id=pid, atid=atid).first()

    if not participante:
        raise HTTPException(status_code=404, detail="Participante não encontrado")

    db.delete(participante)
    db.commit()
    return RedirectResponse(f"/atividade/admin/{atid}/editar", status_code=303)
