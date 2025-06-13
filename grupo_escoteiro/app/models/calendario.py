from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Calendario(Base):
    __tablename__ = "calendario"

    calid = Column(Integer, primary_key=True, index=True)
    calnome = Column(String(100), nullable=False)
    cor = Column(String(20))
    empid = Column(Integer, ForeignKey("empresa.empcod"), nullable=False)

    atividades = relationship("Atividade", back_populates="calendario", cascade="all, delete-orphan")
