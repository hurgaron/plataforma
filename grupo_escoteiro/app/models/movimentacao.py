# models/movimentacao.py

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.database import Base

class Movimentacao(Base):
    __tablename__ = "movimentacao"

    movcod = Column(Integer, primary_key=True, index=True)
    matcod = Column(Integer, ForeignKey("material.matcod"))
    movtipo = Column(String(10))  # 'ENTRADA' ou 'SAIDA'
    movquantidade = Column(Numeric(10, 2))
    movdata = Column(Date)
    movobservacao = Column(String(255))
    empid = Column(Integer, ForeignKey("empresa.empcod"))

    material = relationship("Material", back_populates="movimentacoes")
