from sqlalchemy import Column, Integer, String, Numeric, Date, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Conta(Base):
    __tablename__ = "conta"

    concod = Column(Integer, primary_key=True)
    empid = Column(Integer, ForeignKey("empresa.empcod", ondelete="CASCADE"), nullable=False)
    contipo = Column(String(10), nullable=False)  # 'pagar' ou 'receber'
    condescricao = Column(String(255), nullable=False)
    convalor = Column(Numeric(10, 2), nullable=False)
    convidovenc = Column(Date, nullable=False)
    constatus = Column(String(20), default="pendente")
    conobservacao = Column(Text)
    fornecedor_id = Column(Integer, ForeignKey("fornecedor.forcod"), nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    contdata = Column(Date, nullable=False)

    fornecedor = relationship("Fornecedor", back_populates="contas", lazy="joined")
