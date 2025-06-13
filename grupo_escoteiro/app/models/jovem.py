from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Jovem(Base):
    __tablename__ = "jovem"

    jovcod = Column(Integer, primary_key=True, index=True)
    jovnome = Column(String(100), nullable=False)
    jovdata_nasc = Column(Date, nullable=False)
    empid = Column(Integer, ForeignKey("empresa.empcod", ondelete="CASCADE"), nullable=False)
    
    mensalidades = relationship("Mensalidade", back_populates="jovem")
