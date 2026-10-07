import enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from database import Base


class EstadoEntrada(str, enum.Enum):
    DISPONIBLE = "DISPONIBLE"  # a la venta
    RESERVADA = "RESERVADA"  # retenida por una venta con pago en curso
    EMITIDA = "EMITIDA"  # vendida, con código QR
    ANULADA = "ANULADA"  # dada de baja, no ocupa capacidad


class Entrada(Base):
    __tablename__ = "entradas"

    id = Column(Integer, primary_key=True, index=True)
    sector_id = Column(Integer, ForeignKey("sectores.id"), nullable=False)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=True)
    estado = Column(String, nullable=False, default=EstadoEntrada.DISPONIBLE.value)
    codigo_qr = Column(String, nullable=True, unique=True)  # se genera al emitir
    fecha_emision = Column(DateTime, nullable=True)  # se completa al emitir
