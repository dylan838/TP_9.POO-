import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String

from database import Base


class EstadoVenta(str, enum.Enum):
    PENDIENTE = "PENDIENTE"  # pago en curso, entradas reservadas
    PAGADA = "PAGADA"  # pago aprobado, entradas emitidas
    CANCELADA = "CANCELADA"  # pago rechazado o fallido, entradas liberadas


class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    estado = Column(String, nullable=False, default=EstadoVenta.PENDIENTE.value)
    total = Column(Numeric(12, 2), nullable=False)
    fecha = Column(DateTime, nullable=False, default=datetime.now)
    referencia_pago = Column(String, nullable=True)  # código que devuelve la pasarela
