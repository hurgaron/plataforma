from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Certificado(Base):
    __tablename__ = "certificado"

    certid = Column(Integer, primary_key=True, index=True)
    certnumero = Column(String, nullable=False)
    certtipo = Column(String, nullable=False)
    certdestinatario = Column(String, nullable=False)
    certcategoria = Column(String, nullable=False)  # jovem, adulto, parceiro
    refid = Column(Integer, nullable=True)
    jovem_id = Column(Integer, ForeignKey("jovem.jovcod"), nullable=True)
    certdescricao = Column(String, nullable=True)
    certdata = Column(Date, nullable=False)
    certdata_geracao = Column(Date, nullable=False)
    certdata_entrega = Column(Date, nullable=True)
    empid = Column(Integer, ForeignKey("empresa.empcod"), nullable=False)

    jovem = relationship("Jovem", backref="certificados")
    empresa = relationship("Empresa", back_populates="certificados")
