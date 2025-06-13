from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import date
from starlette.status import HTTP_302_FOUND

from app.database import SessionLocal
from app.auth import obter_usuario_logado
from app.models.mensalidade import Mensalidade
from app.models.jovem import Jovem

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/mensalidades", response_class=HTMLResponse)
def listar_mensalidades(
    request: Request,
    mes: int = 0,
    ano: int = 0,
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    from sqlalchemy import extract

    query = db.query(Mensalidade).join(Jovem).filter(Mensalidade.empid == usuario.empid)
    if mes and ano:
        query = query.filter(
            extract("month", Mensalidade.mendata_venc) == mes,
            extract("year", Mensalidade.mendata_venc) == ano
        )
    
    mensalidades = query.order_by(Mensalidade.mendata_venc).all()
    jovens = db.query(Jovem).filter(Jovem.empid == usuario.empid).all()
    
    return templates.TemplateResponse("mensalidades.html", {
        "request": request,
        "mensalidades": mensalidades,
        "jovens": jovens,
        "mes": mes,
        "ano": ano,
        "usuario": usuario
    })
        

# FORMULÁRIO DE NOVA MENSALIDADE
@router.get("/mensalidades/novo", response_class=HTMLResponse)
def form_mensalidade(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    jovens = db.query(Jovem).filter(Jovem.empid == usuario.empid).all()
    return templates.TemplateResponse("mensalidade_form.html", {
        "request": request,
        "jovens": jovens,
        "usuario": usuario
    })

@router.post("/mensalidades/novo")
def criar_mensalidade(
    jovcod: int = Form(...),
    mendata_venc: date = Form(...),
    menvalor: float = Form(...),
    menobservacao: str = Form(""),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    nova = Mensalidade(
        jovcod=jovcod,
        empid=usuario.empid,
        mendata_venc=mendata_venc,
        menvalor=menvalor,
        menobservacao=menobservacao,
        menstatus="pendente"
    )
    db.add(nova)
    db.commit()
    return RedirectResponse(url="/mensalidades", status_code=HTTP_302_FOUND)

# EDIÇÃO
@router.get("/mensalidades/{menid}/editar", response_class=HTMLResponse)
def editar_mensalidade_form(menid: int, request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    mensalidade = db.query(Mensalidade).filter(Mensalidade.menid == menid, Mensalidade.empid == usuario.empid).first()
    if not mensalidade:
        raise HTTPException(status_code=404, detail="Mensalidade não encontrada")
    return templates.TemplateResponse("mensalidade_editar.html", {"request": request, "mensalidade": mensalidade, "usuario": usuario})

@router.post("/mensalidades/{menid}/editar")
def salvar_edicao_mensalidade(
    menid: int,
    menvalor: float = Form(...),
    mendata_venc: date = Form(...),
    menobservacao: str = Form(""),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    mensalidade = db.query(Mensalidade).filter(Mensalidade.menid == menid, Mensalidade.empid == usuario.empid).first()
    if not mensalidade:
        raise HTTPException(status_code=404, detail="Mensalidade não encontrada")

    mensalidade.menvalor = menvalor
    mensalidade.mendata_venc = mendata_venc
    mensalidade.menobservacao = menobservacao
    db.commit()
    return RedirectResponse(url=f"/mensalidades/{mensalidade.jovcod}", status_code=HTTP_302_FOUND)

# EXCLUSÃO
@router.post("/mensalidades/{menid}/excluir")
def excluir_mensalidade(menid: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    mensalidade = db.query(Mensalidade).filter(Mensalidade.menid == menid, Mensalidade.empid == usuario.empid).first()
    if not mensalidade:
        raise HTTPException(status_code=404, detail="Mensalidade não encontrada")

    jovcod = mensalidade.jovcod
    db.delete(mensalidade)
    db.commit()
    return RedirectResponse(url=f"/mensalidades/{jovcod}", status_code=HTTP_302_FOUND)

# MARCAR COMO PAGO (via AJAX)
@router.post("/mensalidades/{menid}/pagar")
def marcar_como_pago(
    menid: int,
    db: Session = Depends(get_db),
    usuario = Depends(obter_usuario_logado)
):
    mensalidade = db.query(Mensalidade).filter(
        Mensalidade.menid == menid,
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

# GERAÇÃO EM LOTE
@router.post("/mensalidades/lote")
def gerar_mensalidades_lote(
    menvalor: float = Form(...),
    mendata_venc: date = Form(...),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    jovens = db.query(Jovem).filter(Jovem.empid == usuario.empid).all()
    contador = 0

    for jovem in jovens:
        # Evita duplicidade de mensalidade para o mesmo mês
        existe = db.query(Mensalidade).filter(
            Mensalidade.jovcod == jovem.jovcod,
            Mensalidade.mendata_venc == mendata_venc
        ).first()

        if not existe:
            nova = Mensalidade(
                jovcod=jovem.jovcod,
                empid=usuario.empid,
                menvalor=menvalor,
                mendata_venc=mendata_venc,
                menstatus="pendente"
            )
            db.add(nova)
            contador += 1

    db.commit()
    return RedirectResponse(url="/dashboard", status_code=HTTP_302_FOUND)


