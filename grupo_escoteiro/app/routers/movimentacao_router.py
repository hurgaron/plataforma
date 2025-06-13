# routers/movimentacao_router.py

from datetime import date
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.auth import obter_usuario_logado, get_db
from app.models import Movimentacao
from app.models import Material


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/almoxarifado/movimentacoes", response_class=HTMLResponse)
def listar_movimentacoes(
    request: Request,
    busca: str = "",
    tipo: str = "",
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    query = db.query(Movimentacao).join(Material).filter(Movimentacao.empid == usuario.empid)

    if busca:
        query = query.filter(Material.matnome.ilike(f"%{busca}%"))
    
    if tipo in ["ENTRADA", "SAIDA"]:
        query = query.filter(Movimentacao.movtipo == tipo)

    movimentacoes = query.order_by(Movimentacao.movdata.desc()).all()

    return templates.TemplateResponse("movimentacoes.html", {
        "request": request,
        "movimentacoes": movimentacoes,
        "busca": busca,
        "tipo": tipo,
        "usuario": usuario
    })
    
@router.get("/almoxarifado/movimentacoes/nova", response_class=HTMLResponse)
def nova_movimentacao(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    materiais = db.query(Material).filter(Material.empid == usuario.empid).order_by(Material.matnome).all()
    hoje = date.today()
    return templates.TemplateResponse("movimentacao_form.html", {
        "request": request,
        "materiais": materiais,
        "usuario": usuario,
        "hoje": hoje
    })
    
@router.post("/almoxarifado/movimentacoes/nova")
def criar_movimentacao(
    request: Request,
    matcod: int = Form(...),
    movtipo: str = Form(...),
    movquantidade: float = Form(...),
    movdata: date = Form(...),
    movobservacao: str = Form(""),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    material = db.query(Material).filter(Material.matcod == matcod, Material.empid == usuario.empid).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado.")

    if movtipo == "ENTRADA":
        material.matquantidade += movquantidade
    elif movtipo == "SAIDA":
        if material.matquantidade < movquantidade:
            raise HTTPException(status_code=400, detail="Quantidade insuficiente em estoque.")
        material.matquantidade -= movquantidade

    nova = Movimentacao(
        matcod=matcod,
        movtipo=movtipo,
        movquantidade=movquantidade,
        movdata=movdata,
        movobservacao=movobservacao,
        empid=usuario.empid
    )
    db.add(nova)
    db.commit()

    return RedirectResponse(url="/almoxarifado/movimentacoes", status_code=303)

@router.get("/almoxarifado/movimentacoes/material/{matcod}", response_class=HTMLResponse)
def historico_por_material(
    request: Request,
    matcod: int,
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    material = db.query(Material).filter(Material.matcod == matcod, Material.empid == usuario.empid).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado")

    movimentacoes = (
        db.query(Movimentacao)
        .filter(Movimentacao.empid == usuario.empid, Movimentacao.matcod == matcod)
        .order_by(Movimentacao.movdata.desc())
        .all()
    )
    
    movimentacoes = sorted(movimentacoes, key=lambda x: x.movdata)

    return templates.TemplateResponse("movimentacoes_material.html", {
        "request": request,
        "material": material,
        "movimentacoes": movimentacoes,
        "usuario": usuario
    })
