from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy.orm import Session

from exceptions import (
    CantidadInvalidaError,
    CapacidadInsuficienteError,
    ReglaNegocioError,
)
from models.evento import Evento
from models.sector import Sector
from schemas.cotizacion_schema import CotizacionRequest, CotizacionResponse
from services import evento_service, sector_service

_DOS_DECIMALES = Decimal("0.01")


def _validar_cantidad(cantidad: int) -> None:
    if cantidad <= 0:
        raise CantidadInvalidaError("Cantidad inválida")


def _validar_sector_pertenece_a_evento(sector: Sector, evento: Evento) -> None:
    if sector.evento_id != evento.id:
        raise ReglaNegocioError(
            f"El sector '{sector.nombre}' no pertenece al evento '{evento.nombre}'"
        )


def _validar_disponibilidad(db: Session, sector: Sector, cantidad: int) -> None:
    disponibles = sector_service.obtener_disponibilidad(db, sector)
    if cantidad > disponibles:
        raise CapacidadInsuficienteError(
            f"Capacidad insuficiente: se solicitaron {cantidad} entradas "
            f"y solo quedan {disponibles} en el sector '{sector.nombre}'"
        )


def _calcular_subtotal(precio_unitario: Decimal, cantidad: int) -> Decimal:
    return (precio_unitario * cantidad).quantize(_DOS_DECIMALES, rounding=ROUND_HALF_UP)


def cotizar(db: Session, datos: CotizacionRequest) -> CotizacionResponse:
    """Calcula el costo total exacto de una compra, sin reservar ni cobrar nada."""
    _validar_cantidad(datos.cantidad)

    evento = evento_service.obtener_evento(db, datos.evento_id)
    sector = sector_service.obtener_sector(db, datos.sector_id)

    _validar_sector_pertenece_a_evento(sector, evento)
    _validar_disponibilidad(db, sector, datos.cantidad)

    subtotal = _calcular_subtotal(sector.precio, datos.cantidad)

    return CotizacionResponse(
        evento_id=evento.id,
        evento_nombre=evento.nombre,
        sector_id=sector.id,
        sector_nombre=sector.nombre,
        cantidad=datos.cantidad,
        precio_unitario=sector.precio,
        subtotal=subtotal,
        total=subtotal,  # hoy no hay cargos extra; aquí se sumarían a futuro
    )
