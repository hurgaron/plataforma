from sqlalchemy import Boolean, Column, Integer, Numeric, String, Date, ForeignKey, Enum as SqlEnum
from app.models.enums import TipoLancamentoEnum  # importa o enum
from sqlalchemy.orm import relationship
from app.database import Base

class AtividadeCusto(Base):
    __tablename__ = "atividade_custo"

    id = Column(Integer, primary_key=True)
    atid = Column(Integer, ForeignKey("atividade.atid", ondelete="CASCADE"), nullable=False)
    descricao = Column(String(100), nullable=False)
    tipo = Column(String(20))
    quantidade = Column(Numeric(10, 2), nullable=False)
    valor_unitario = Column(Numeric(10, 2), nullable=False)
    empid = Column(Integer, ForeignKey("empresa.empcod"), nullable=False)

    tipo_lancamento = Column(SqlEnum(TipoLancamentoEnum), nullable=False, default=TipoLancamentoEnum.previsto)

    atividade = relationship("Atividade", back_populates="custos")