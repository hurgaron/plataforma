
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.models import Adulto
from app.auth import get_db, obter_usuario_logado


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/adultos", response_class=HTMLResponse)
def listar_adultos(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    adultos = db.query(Adulto).filter(Adulto.empid == usuario.empid).all()
    return templates.TemplateResponse("adultos.html", {"request": request, "adultos": adultos, "usuario": usuario})

@router.get("/adultos/novo", response_class=HTMLResponse)
def novo_adulto(request: Request, usuario=Depends(obter_usuario_logado)):
    return templates.TemplateResponse("adultos_novo.html", {"request": request, "usuario": usuario})

@router.post("/adultos/novo")
def criar_adulto(
    adunome: str = Form(...),
    adudata_nasc: str = Form(...),
    adutelefone: str = Form(None),
    aduemail: str = Form(None),
    aduendereco: str = Form(None),
    aduregistro: str = Form(None),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    adulto = Adulto(
        adunome=adunome,
        adudata_nasc=adudata_nasc,
        adutelefone=adutelefone,
        aduemail=aduemail,
        aduendereco=aduendereco,
        aduregistro=aduregistro,
        empid=usuario.empid
    )
    db.add(adulto)
    db.commit()
    return RedirectResponse("/adultos", status_code=303)

@router.get("/adultos/{aducod}/editar", response_class=HTMLResponse)
def editar_adulto(aducod: int, request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    adulto = db.query(Adulto).filter(Adulto.aducod == aducod).first()
    return templates.TemplateResponse("adultos_editar.html", {"request": request, "adulto": adulto, "usuario": usuario})

@router.post("/adultos/{aducod}/editar")
def atualizar_adulto(
    aducod: int,
    adunome: str = Form(...),
    adudata_nasc: str = Form(...),
    adutelefone: str = Form(None),
    aduemail: str = Form(None),
    aduendereco: str = Form(None),
    aduregistro: str = Form(None),
    db: Session = Depends(get_db)
):
    adulto = db.query(Adulto).filter(Adulto.aducod == aducod).first()
    adulto.adunome = adunome
    adulto.adudata_nasc = adudata_nasc
    adulto.adutelefone = adutelefone
    adulto.aduemail = aduemail
    adulto.aduendereco = aduendereco
    adulto.aduregistro = aduregistro
    db.commit()
    return RedirectResponse("/adultos", status_code=303)
