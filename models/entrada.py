import enum
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from database import Base


class EstadoEntrada(str, enum.Enum):
    DISPONIBLE = "DISPONIBLE"  # a la venta
    RESERVADA = "RESERVADA"  # retenida por una venta con pago en curso
    EMITIDA = "EMITIDA"  # vendida y pagada: habilitada para ingresar
    UTILIZADA = "UTILIZADA"  # ya se usó para ingresar (no se puede reutilizar)
    ANULADA = "ANULADA"  # dada de baja, no ocupa capacidad


class Entrada(Base):
    __tablename__ = "entradas"

    id = Column(Integer, primary_key=True, index=True)
    sector_id = Column(Integer, ForeignKey("sectores.id"), nullable=False)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=True)
    estado = Column(String, nullable=False, default=EstadoEntrada.DISPONIBLE.value)
    # Identidad de la entrada: existe desde que se genera. Solo es válida para
    # ingresar cuando el estado es EMITIDA (lo decide acceso_service).
    codigo_qr = Column(String, nullable=False, unique=True, default=lambda: uuid4().hex)
    fecha_emision = Column(DateTime, nullable=True)  # al pagar
    fecha_ingreso = Column(DateTime, nullable=True)  # al escanear en puerta
