from sqlalchemy import Column, Integer, Numeric, Date, String, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.database import Base

class Mensalidade(Base):
    __tablename__ = "mensalidade"

    menid = Column(Integer, primary_key=True, index=True)
    jovcod = Column(Integer, ForeignKey("jovem.jovcod", ondelete="CASCADE"), nullable=False)
    empid = Column(Integer, ForeignKey("empresa.empcod", ondelete="CASCADE"), nullable=False)
    menvalor = Column(Numeric(10, 2), nullable=False)
    mendata_venc = Column(Date, nullable=False)
    menstatus = Column(String(20), default="pendente")  # pendente, pago, cancelado
    menobservacao = Column(Text)
    mencreated_at = Column(TIMESTAMP, server_default=func.now())

    jovem = relationship("Jovem", back_populates="mensalidades")