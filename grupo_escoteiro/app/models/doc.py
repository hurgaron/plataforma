from sqlalchemy import Column, Integer, String, Numeric, Date, Boolean, ForeignKey
from app.database import Base

class Doc(Base):
    __tablename__ = "doc"

    doccod = Column(Integer, primary_key=True, index=True)
    docdesc = Column(String(255), nullable=False)
    doctipo = Column(String(10), nullable=False)  # pagar / receber
    valor = Column(Numeric(10, 2), nullable=False)
    vencimento = Column(Date, nullable=False)
    pago = Column(Boolean, default=False)
    parceiro_id = Column(Integer, nullable=True)
    empid = Column(Integer, ForeignKey("empresa.empcod", ondelete="CASCADE"), nullable=False)
