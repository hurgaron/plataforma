from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuario"

    usucod = Column(Integer, primary_key=True, index=True)
    usunome = Column(String(100), nullable=False)
    usuemail = Column(String(100), unique=True, nullable=False)
    ususenha = Column(String(255), nullable=False)
    usufuncao = Column(String(20), nullable=False, default="colaborador")
    empid = Column(Integer, ForeignKey("empresa.empcod", ondelete="CASCADE"), nullable=False)

    empresa = relationship("Empresa", back_populates="usuarios")
