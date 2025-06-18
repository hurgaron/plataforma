from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.database import Base

class Adulto(Base):
    __tablename__ = "adulto"

    aducod = Column(Integer, primary_key=True, index=True)
    adunome = Column(String, nullable=False)
    adudata_nasc = Column(Date, nullable=False)
    adutelefone = Column(String)
    aduemail = Column(String)
    aduendereco = Column(String)
    aduregistro = Column(String)
    empid = Column(Integer, ForeignKey("empresa.empcod"), nullable=False)
