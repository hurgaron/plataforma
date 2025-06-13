from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.database import Base

class Adulto(Base):
    __tablename__ = "adulto"

    aducod = Column(Integer, primary_key=True, index=True)
    adunome = Column(String(100), nullable=False)
    adudata_nasc = Column(Date, nullable=False)
    empid = Column(Integer, ForeignKey("empresa.empcod", ondelete="CASCADE"), nullable=False)
