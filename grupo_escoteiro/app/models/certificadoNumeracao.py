from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class CertificadoNumeracao(Base):
    __tablename__ = "certificado_numeracao"

    numid = Column(Integer, primary_key=True, index=True)
    prefixo = Column(String, nullable=False)
    sequencia_atual = Column(Integer, nullable=False, default=1)
    descricao = Column(String)
    empid = Column(Integer, ForeignKey("empresa.empcod"), nullable=False)

    empresa = relationship("Empresa", back_populates="numeracoes")
