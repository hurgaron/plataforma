from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.empresa import Empresa
from app.auth import obter_usuario_logado
from starlette.status import HTTP_303_SEE_OTHER

router = APIRouter(prefix="/empresa", tags=["Empresa"])
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/criar")
def criar_empresa(empnome: str, empcnpj: str, db: Session = Depends(get_db)):
    existente = db.query(Empresa).filter(Empresa.empcnpj == empcnpj).first()
    if existente:
        raise HTTPException(status_code=400, detail="Empresa já cadastrada.")
    nova = Empresa(empnome=empnome, empcnpj=empcnpj)
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

@router.get("/editar", response_class=HTMLResponse)
def editar_empresa_form(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    empresa = db.query(Empresa).filter(Empresa.empcod == usuario.empid).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return templates.TemplateResponse("empresa/form.html", {"request": request, "empresa": empresa})

@router.post("/editar")
def editar_empresa(
    empnome: str = Form(...),
    empcnpj: str = Form(...),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    empresa = db.query(Empresa).filter(Empresa.empcod == usuario.empid).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    empresa.empnome = empnome
    empresa.empcnpj = empcnpj
    db.commit()
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)