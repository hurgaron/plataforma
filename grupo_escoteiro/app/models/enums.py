import enum

class TipoLancamentoEnum(str, enum.Enum):
    previsto = "previsto"
    realizado = "realizado"