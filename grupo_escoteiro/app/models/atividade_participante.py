from sqlalchemy import Boolean, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class AtividadeParticipante(Base):
    __tablename__ = "atividade_participante"

    id = Column(Integer, primary_key=True)
    atid = Column(Integer, ForeignKey("atividade.atid", ondelete="CASCADE"), nullable=False)
    tipo = Column(String(10), nullable=False)  # 'jovem' ou 'adulto'
    pessoa_id = Column(Integer, nullable=False)
    presenca = Column(Boolean, default=True)
    observacao = Column(String(255))
    empid = Column(Integer, ForeignKey("empresa.empcod"), nullable=False)

    atividade = relationship("Atividade", back_populates="participantes")
