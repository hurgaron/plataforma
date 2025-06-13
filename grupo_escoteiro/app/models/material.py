from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Material(Base):
    __tablename__ = "material"

    matcod = Column(Integer, primary_key=True, index=True)
    matnome = Column(String(100), nullable=False)
    matcod_barras = Column(String(50), nullable=True)
    matunidade = Column(String(20), nullable=True)
    matquantidade = Column(Float, nullable=False, default=0)
    matcategoria = Column(String(50), nullable=True)
    matfoto_url = Column(String(255), nullable=True)

    empid = Column(Integer, ForeignKey("empresa.empcod", ondelete="CASCADE"), nullable=False)
    movimentacoes = relationship("Movimentacao", back_populates="material", lazy="joined")

