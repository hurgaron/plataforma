from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Fornecedor(Base):
    __tablename__ = "fornecedor"

    forcod = Column(Integer, primary_key=True, index=True)
    fornome = Column(String(100), nullable=False)
    forcnpj = Column(String(18), nullable=True)
    foremail = Column(String(100), nullable=True)
    empid = Column(Integer, ForeignKey("empresa.empcod", ondelete="CASCADE"), nullable=False)
    
    contas = relationship("Conta", back_populates="fornecedor")
