from fastapi import APIRouter, Query, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.auth import get_db, obter_usuario_logado
from app.models import Certificado, Jovem, CertificadoNumeracao
from datetime import date, datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/certificados", response_class=HTMLResponse)
def listar_certificados(
    request: Request,
    busca: str = Query("", alias="busca"),
    entregue: str = Query("", alias="entregue"),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    query = db.query(Certificado).filter(Certificado.empid == usuario.empid)

    if busca:
        busca_like = f"%{busca}%"
        query = query.filter(Certificado.certdestinatario.ilike(busca_like))

    if entregue == "sim":
        query = query.filter(Certificado.certdata_entrega.isnot(None))
    elif entregue == "nao":
        query = query.filter(Certificado.certdata_entrega.is_(None))

    certificados = query.order_by(Certificado.certdata.desc()).all()

    return templates.TemplateResponse("certificados.html", {
        "request": request,
        "certificados": certificados,
        "busca": busca,
        "entregue": entregue,
        "usuario": usuario
    })

@router.get("/certificados/novo", response_class=HTMLResponse)
def novo_certificado(request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    tipos = db.query(Certificado.certtipo).filter(Certificado.empid == usuario.empid).distinct().all()
    tipos_existentes = [t[0] for t in tipos]
    jovens = db.query(Jovem).filter(Jovem.empid == usuario.empid).order_by(Jovem.jovnome).all()
    numeracoes = db.query(CertificadoNumeracao).filter(CertificadoNumeracao.empid == usuario.empid).all()
    return templates.TemplateResponse("certificado_form.html", {
        "request": request,
        "cert": {},
        "tipos_existentes": tipos_existentes,
        "jovens": jovens,
        "numeracoes": numeracoes,
        "now": datetime.now(),
        "usuario": usuario
    })

@router.post("/certificados/novo")
def salvar_certificado(
    request: Request,
    certnumero: str = Form(None),
    certtipo: str = Form(...),
    certdestinatario: str = Form(...),
    certcategoria: str = Form(...),
    jovem_id: str = Form(None),
    numeracao_id: str = Form(None),
    certdescricao: str = Form(None),
    certdata: date = Form(...),
    certdata_geracao: date = Form(...),
    certdata_entrega: str = Form(None),  # recebida como string
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    # tratar certdata_entrega vazia
    from datetime import datetime
    if not certdata_entrega:
        certdata_entrega = None
    else:
        certdata_entrega = datetime.strptime(certdata_entrega, "%Y-%m-%d").date()

    # Gerar número automático se necessário
    if not certnumero and numeracao_id:
        numeracao = db.query(CertificadoNumeracao).filter_by(numid=int(numeracao_id)).first()
        certnumero = f"{numeracao.prefixo}{numeracao.sequencia_atual:03d}"
        numeracao.sequencia_atual += 1
        db.add(numeracao)

    cert = Certificado(
        certnumero=certnumero,
        certtipo=certtipo,
        certdestinatario=certdestinatario,
        certcategoria=certcategoria,
        jovem_id=int(jovem_id) if jovem_id else None,
        certdescricao=certdescricao,
        certdata=certdata,
        certdata_geracao=certdata_geracao,
        certdata_entrega=certdata_entrega,
        empid=usuario.empid
    )
    db.add(cert)
    db.commit()
    return RedirectResponse(url="/certificados", status_code=303)

@router.get("/certificados/{certid}/editar", response_class=HTMLResponse)
def editar_certificado(certid: int, request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    cert = db.query(Certificado).filter(Certificado.certid == certid, Certificado.empid == usuario.empid).first()
    tipos = db.query(Certificado.certtipo).filter(Certificado.empid == usuario.empid).distinct().all()
    tipos_existentes = [t[0] for t in tipos]
    jovens = db.query(Jovem).filter(Jovem.empid == usuario.empid).order_by(Jovem.jovnome).all()
    numeracoes = db.query(CertificadoNumeracao).filter(CertificadoNumeracao.empid == usuario.empid).all()
    return templates.TemplateResponse("certificado_form.html", {
        "request": request,
        "cert": cert,
        "tipos_existentes": tipos_existentes,
        "jovens": jovens,
        "numeracoes": numeracoes
    })

@router.get("/certificados/{certid}/imprimir", response_class=HTMLResponse)
def imprimir_certificado(certid: int, request: Request, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    cert = db.query(Certificado).filter(Certificado.certid == certid, Certificado.empid == usuario.empid).first()
    return templates.TemplateResponse("certificado_impressao.html", {"request": request, "cert": cert})

@router.post("/certificados/{certid}/editar")
def atualizar_certificado(
    certid: int,
    request: Request,
    certnumero: str = Form(...),
    certtipo: str = Form(...),
    certdestinatario: str = Form(...),
    certcategoria: str = Form(...),
    jovem_id: str = Form(None),
    numeracao_id: str = Form(None),
    certdescricao: str = Form(None),
    certdata: date = Form(...),
    certdata_geracao: date = Form(...),
    certdata_entrega: str = Form(None),
    db: Session = Depends(get_db),
    usuario=Depends(obter_usuario_logado)
):
    from datetime import datetime
    if not certdata_entrega:
        certdata_entrega = None
    else:
        certdata_entrega = datetime.strptime(certdata_entrega, "%Y-%m-%d").date()

    cert = db.query(Certificado).filter(Certificado.certid == certid, Certificado.empid == usuario.empid).first()
    if not cert:
        return RedirectResponse(url="/certificados", status_code=303)

    cert.certnumero = certnumero
    cert.certtipo = certtipo
    cert.certdestinatario = certdestinatario
    cert.certcategoria = certcategoria
    cert.jovem_id = int(jovem_id) if jovem_id else None
    cert.certdescricao = certdescricao
    cert.certdata = certdata
    cert.certdata_geracao = certdata_geracao
    cert.certdata_entrega = certdata_entrega

    db.commit()
    return RedirectResponse(url="/certificados", status_code=303)
