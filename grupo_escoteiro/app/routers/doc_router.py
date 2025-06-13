from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import SessionLocal
from app.models.doc import Doc
from app.auth import obter_usuario_logado
from pydantic import BaseModel

router = APIRouter(prefix="/financeiro", tags=["Financeiro"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DocCreate(BaseModel):
    docdesc: str
    doctipo: str  # pagar / receber
    valor: float
    vencimento: date
    parceiro_id: Optional[int] = None

class DocOut(BaseModel):
    doccod: int
    docdesc: str
    doctipo: str
    valor: float
    vencimento: date
    pago: bool
    parceiro_id: Optional[int]

    class Config:
        orm_mode = True

@router.post("/", response_model=DocOut)
def criar_documento(dados: DocCreate, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    if dados.doctipo not in ["pagar", "receber"]:
        raise HTTPException(status_code=400, detail="Tipo deve ser 'pagar' ou 'receber'")
    doc = Doc(**dados.dict(), empid=usuario.empid)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@router.get("/", response_model=List[DocOut])
def listar_documentos(tipo: Optional[str] = None, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    query = db.query(Doc).filter(Doc.empid == usuario.empid)
    if tipo in ["pagar", "receber"]:
        query = query.filter(Doc.doctipo == tipo)
    return query.order_by(Doc.vencimento).all()

@router.put("/{doccod}/pagar")
def marcar_como_pago(doccod: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    doc = db.query(Doc).filter(Doc.doccod == doccod, Doc.empid == usuario.empid).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    doc.pago = True
    db.commit()
    return {"detail": "Documento marcado como pago"}

@router.delete("/{doccod}")
def deletar_documento(doccod: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    doc = db.query(Doc).filter(Doc.doccod == doccod, Doc.empid == usuario.empid).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    db.delete(doc)
    db.commit()
    return {"detail": "Documento deletado com sucesso"}
