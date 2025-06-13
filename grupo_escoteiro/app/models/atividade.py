from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Atividade(Base):
    __tablename__ = "atividade"

    atid = Column(Integer, primary_key=True, index=True)
    calid = Column(Integer, ForeignKey("calendario.calid"), nullable=False)
    titulo = Column(String(100), nullable=False)
    descricao = Column(Text)
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=False)
    local = Column(String(150))
    criado_por = Column(Integer, ForeignKey("usuario.usucod"))
    criado_em = Column(DateTime, default=datetime.utcnow)
    empid = Column(Integer, ForeignKey("empresa.empcod"), nullable=False)

    calendario = relationship("Calendario", back_populates="atividades")
