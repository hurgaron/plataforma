
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.auth import get_db, obter_usuario_logado
from app.models import Jovem
from datetime import date


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def jovem_para_dict(jovem: Jovem):
    return {
        "jovcod": jovem.jovcod,
        "jovnome": jovem.jovnome,
        "jovdata_nasc": jovem.jovdata_nasc.strftime('%Y-%m-%d') if isinstance(jovem.jovdata_nasc, date) else '',
        "jovregistro": jovem.jovregistro or '',
        "jovtelefone": jovem.jovtelefone or '',
        "jovemail": jovem.jovemail or '',
        "jovendereco": jovem.jovendereco or '',
        "resp_nome": jovem.resp_nome or '',
        "resp_telefone": jovem.resp_telefone or '',
        "resp_email": jovem.resp_email or ''
    }

@router.get("/jovens", response_class=HTMLResponse)
def listar_jovens(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    jovens = db.query(Jovem).filter(Jovem.empid == usuario.empid).all()
    jovens_serializados = [jovem_para_dict(j) for j in jovens]
    return templates.TemplateResponse("jovens.html", {
        "request": request,
        "jovens": jovens_serializados,
        "usuario": usuario
    })

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
    jovem.jovnome = jovnome # type: ignore
    jovem.jovdata_nasc = jovdata_nasc # type: ignore
    jovem.jovtelefone = jovtelefone # type: ignore
    jovem.jovemail = jovemail # type: ignore
    jovem.jovendereco = jovemendereco # type: ignore
    jovem.jovregistro = jovregistro # type: ignore
    jovem.resp_nome = resp_nome # type: ignore
    jovem.resp_telefone = resp_telefone # type: ignore
    jovem.resp_email = resp_email # type: ignore
    db.commit()
    return RedirectResponse("/jovens", status_code=303)
