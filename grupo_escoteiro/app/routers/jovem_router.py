
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.auth import get_db, obter_usuario_logado
from app.models import Jovem


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/jovens", response_class=HTMLResponse)
def listar_jovens(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    jovens = db.query(Jovem).filter(Jovem.empid == usuario.empid).all()
    return templates.TemplateResponse("jovens.html", {"request": request, "jovens": jovens, "usuario": usuario})

@router.get("/jovens/novo", response_class=HTMLResponse)
def novo_jovem(request: Request, usuario=Depends(obter_usuario_logado)):
    return templates.TemplateResponse("jovens_novo.html", {"request": request, "usuario": usuario})

@router.post("/jovens/novo")
def criar_jovem(
    jovnome: str = Form(...),
    jovdata_nasc: str = Form(...),
    jovtelefone: str = Form(None),
    jovemail: str = Form(None),
    jovemendereco: str = Form(None),
    jovregistro: str = Form(None),
    resp_nome: str = Form(None),
    resp_telefone: str = Form(None),
    resp_email: str = Form(None),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    jovem = Jovem(
        jovnome=jovnome,
        jovdata_nasc=jovdata_nasc,
        jovtelefone=jovtelefone,
        jovemail=jovemail,
        jovendereco=jovemendereco,
        jovregistro=jovregistro,
        resp_nome=resp_nome,
        resp_telefone=resp_telefone,
        resp_email=resp_email,
        empid=usuario.empid
    )
    db.add(jovem)
    db.commit()
    return RedirectResponse("/jovens", status_code=303)

@router.get("/jovens/{jovcod}/editar", response_class=HTMLResponse)
def editar_jovem(jovcod: int, request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    jovem = db.query(Jovem).filter(Jovem.jovcod == jovcod).first()
    return templates.TemplateResponse("jovens_editar.html", {"request": request, "jovem": jovem, "usuario": usuario})

@router.post("/jovens/{jovcod}/editar")
def atualizar_jovem(
    jovcod: int,
    jovnome: str = Form(...),
    jovdata_nasc: str = Form(...),
    jovtelefone: str = Form(None),
    jovemail: str = Form(None),
    jovemendereco: str = Form(None),
    jovregistro: str = Form(None),
    resp_nome: str = Form(None),
    resp_telefone: str = Form(None),
    resp_email: str = Form(None),
    db: Session = Depends(get_db)
):
    jovem = db.query(Jovem).filter(Jovem.jovcod == jovcod).first()
    jovem.jovnome = jovnome
    jovem.jovdata_nasc = jovdata_nasc
    jovem.jovtelefone = jovtelefone
    jovem.jovemail = jovemail
    jovem.jovendereco = jovemendereco
    jovem.jovregistro = jovregistro
    jovem.resp_nome = resp_nome
    jovem.resp_telefone = resp_telefone
    jovem.resp_email = resp_email
    db.commit()
    return RedirectResponse("/jovens", status_code=303)
