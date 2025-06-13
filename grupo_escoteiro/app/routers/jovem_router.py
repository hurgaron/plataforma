from fastapi import APIRouter, Request, Depends, Form, HTTPException, Path
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.database import SessionLocal
from app.auth import obter_usuario_logado
from app.models.jovem import Jovem
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 📄 Pydantic para API
class JovemOut(BaseModel):
    jovcod: int
    jovnome: str
    jovdata_nasc: date

    class Config:
        orm_mode = True

class JovemCreate(BaseModel):
    jovnome: str
    jovdata_nasc: date

# 🖥️ Visual HTML
@router.get("/jovens", response_class=HTMLResponse)
def listar_jovens_html(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    jovens = db.query(Jovem).filter(Jovem.empid == usuario.empid).order_by(Jovem.jovnome).all()
    return templates.TemplateResponse("jovens.html", {"request": request, "jovens": jovens, "usuario": usuario})

# 📦 API - GET
@router.get("/api/jovens", response_model=List[JovemOut])
def listar_jovens_api(db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    return db.query(Jovem).filter(Jovem.empid == usuario.empid).order_by(Jovem.jovnome).all()

# 📦 API - POST
@router.post("/api/jovens", response_model=JovemOut)
def criar_jovem_api(dados: JovemCreate, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    novo = Jovem(**dados.dict(), empid=usuario.empid)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

# 📄 Formulário visual para cadastro
@router.get("/jovens/novo", response_class=HTMLResponse)
def novo_jovem_form(request: Request, usuario=Depends(obter_usuario_logado)):
    return templates.TemplateResponse("jovens_novo.html", {"request": request, "usuario": usuario})

# 💾 Submissão do formulário
@router.post("/jovens/novo")
def salvar_jovem_form(
    jovnome: str = Form(...),
    jovdata_nasc: date = Form(...),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    novo = Jovem(jovnome=jovnome, jovdata_nasc=jovdata_nasc, empid=usuario.empid)
    db.add(novo)
    db.commit()
    return RedirectResponse(url="/jovens", status_code=HTTP_302_FOUND)

@router.get("/jovens/{jovcod}/editar", response_class=HTMLResponse)
def editar_jovem_form(jovcod: int, request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    jovem = db.query(Jovem).filter(Jovem.jovcod == jovcod, Jovem.empid == usuario.empid).first()
    if not jovem:
        raise HTTPException(status_code=404, detail="Jovem não encontrado")
    return templates.TemplateResponse("jovens_editar.html", {"request": request, "jovem": jovem, "usuario": usuario})

@router.post("/jovens/{jovcod}/editar")
def salvar_edicao_jovem(
    jovcod: int,
    jovnome: str = Form(...),
    jovdata_nasc: date = Form(...),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    jovem = db.query(Jovem).filter(Jovem.jovcod == jovcod, Jovem.empid == usuario.empid).first()
    if not jovem:
        raise HTTPException(status_code=404, detail="Jovem não encontrado")
    jovem.jovnome = jovnome
    jovem.jovdata_nasc = jovdata_nasc
    db.commit()
    return RedirectResponse(url="/jovens", status_code=HTTP_302_FOUND)

@router.post("/jovens/{jovcod}/excluir")
def excluir_jovem(jovcod: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    jovem = db.query(Jovem).filter(Jovem.jovcod == jovcod, Jovem.empid == usuario.empid).first()
    if not jovem:
        raise HTTPException(status_code=404, detail="Jovem não encontrado")
    db.delete(jovem)
    db.commit()
    return RedirectResponse(url="/jovens", status_code=HTTP_302_FOUND)