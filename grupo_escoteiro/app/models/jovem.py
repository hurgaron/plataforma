from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Jovem(Base):
    __tablename__ = "jovem"

    jovcod = Column(Integer, primary_key=True, index=True)
    jovnome = Column(String, nullable=False)
    jovdata_nasc = Column(Date, nullable=False)
    jovtelefone = Column(String)
    jovemail = Column(String)
    jovendereco = Column(String)
    jovregistro = Column(String)
    resp_nome = Column(String)
    resp_telefone = Column(String)
    resp_email = Column(String)
    empid = Column(Integer, ForeignKey("empresa.empcod"), nullable=False)
    
    mensalidades = relationship("Mensalidade", back_populates="jovem")
