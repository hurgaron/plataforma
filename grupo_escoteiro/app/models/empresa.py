from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Empresa(Base):
    __tablename__ = "empresa"

    empcod = Column(Integer, primary_key=True, index=True)
    empnome = Column(String(100), nullable=False)
    empcnpj = Column(String(18), unique=True, nullable=False)
    empativo = Column(Boolean, default=True)

    usuarios = relationship("Usuario", back_populates="empresa", cascade="all, delete")
    certificados = relationship("Certificado", back_populates="empresa")
    numeracoes = relationship("CertificadoNumeracao", back_populates="empresa")