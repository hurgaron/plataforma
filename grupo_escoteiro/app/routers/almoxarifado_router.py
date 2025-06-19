from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND

from app.database import SessionLocal
from app.auth import obter_usuario_logado, get_db
from app.models.material import Material

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/almoxarifado", response_class=HTMLResponse)
def listar_materiais(request: Request, busca: str = "", db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    query = db.query(Material).filter(Material.empid == usuario.empid)

    if busca:
        busca_like = f"%{busca}%"
        query = query.filter(
            Material.matnome.ilike(busca_like) | Material.matcod_barras.ilike(busca_like)
        )

    materiais = query.order_by(Material.matnome).all()

    return templates.TemplateResponse("materiais.html", {
        "request": request,
        "materiais": materiais,
        "busca": busca,
        "usuario": usuario
    })

@router.get("/almoxarifado/novo", response_class=HTMLResponse)
def novo_material_form(request: Request, usuario = Depends(obter_usuario_logado)):
    return templates.TemplateResponse("material_form.html", {
        "request": request,
        "material": None,
        "usuario": usuario
    })

@router.post("/almoxarifado/novo")
def criar_material(
    matnome: str = Form(...),
    matdescricao: str = Form(""),
    matquantidade: int = Form(...),
    matcod_barras: str = Form(""),
    matfoto_url: str = Form(""),
    db: Session = Depends(get_db),
    usuario = Depends(obter_usuario_logado)
):
    material = Material(
        empid=usuario.empid,
        matnome=matnome,
        matdescricao=matdescricao,
        matquantidade=matquantidade,
        matcod_barras=matcod_barras,
        matfoto_url=matfoto_url
    )
    db.add(material)
    db.commit()
    return RedirectResponse(url="/almoxarifado", status_code=HTTP_302_FOUND)

@router.get("/almoxarifado/{matcod}/editar", response_class=HTMLResponse)
def editar_material_form(matcod: int, request: Request, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    material = db.query(Material).filter(Material.matcod == matcod, Material.empid == usuario.empid).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado")
    return templates.TemplateResponse("material_form.html", {
        "request": request,
        "material": material,
        "usuario": usuario
    })

@router.post("/almoxarifado/{matcod}/editar")
def salvar_edicao_material(
    matcod: int,
    matnome: str = Form(...),
    matdescricao: str = Form(""),
    matquantidade: int = Form(...),
    matcod_barras: str = Form(""),
    matfoto_url: str = Form(""),
    db: Session = Depends(get_db),
    usuario = Depends(obter_usuario_logado)
):
    material = db.query(Material).filter(Material.matcod == matcod, Material.empid == usuario.empid).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado")

    material.matnome = matnome
    material.matdescricao = matdescricao
    material.matquantidade = matquantidade
    material.matcod_barras = matcod_barras
    material.matfoto_url = matfoto_url
    db.commit()
    return RedirectResponse(url="/almoxarifado", status_code=HTTP_302_FOUND)

@router.post("/almoxarifado/{matcod}/excluir")
def excluir_material(matcod: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    material = db.query(Material).filter(Material.matcod == matcod, Material.empid == usuario.empid).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado")

    db.delete(material)
    db.commit()
    return RedirectResponse(url="/almoxarifado", status_code=HTTP_302_FOUND)
