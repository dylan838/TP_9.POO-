from sqlalchemy import select
from sqlalchemy.orm import Session

from exceptions import (
    CapacidadInsuficienteError,
    ConflictoError,
    RecursoNoEncontradoError,
    ReglaNegocioError,
)
from models.entrada import Entrada, EstadoEntrada
from schemas.entrada_schema import EntradaCreate, EntradaLoteCreate, EntradaUpdate
from services import sector_service

# Estados que pertenecen a una venta: los gestionan pago_service y acceso_service
_ESTADOS_DE_PAGO = {
    EstadoEntrada.RESERVADA.value,
    EstadoEntrada.EMITIDA.value,
    EstadoEntrada.UTILIZADA.value,
}


def _validar_cupo(db: Session, sector_id: int, cantidad: int = 1) -> None:
    """Verifica que el sector admita `cantidad` entradas más sin superar su capacidad."""
    sector = sector_service.obtener_sector(db, sector_id)
    cupo = sector.capacidad - sector_service.contar_entradas_vigentes(db, sector_id)
    if cantidad > cupo:
        raise CapacidadInsuficienteError(
            f"Capacidad insuficiente: el sector '{sector.nombre}' admite {cupo} entradas más"
        )


def crear_entrada(db: Session, data: EntradaCreate) -> Entrada:
    """Genera una entrada DISPONIBLE (a la venta) en el sector."""
    _validar_cupo(db, data.sector_id)
    nueva = Entrada(sector_id=data.sector_id, estado=EstadoEntrada.DISPONIBLE.value)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


def crear_entradas_en_lote(db: Session, data: EntradaLoteCreate) -> list[Entrada]:
    """Genera varias entradas DISPONIBLES de una vez (hasta completar la capacidad)."""
    _validar_cupo(db, data.sector_id, data.cantidad)
    nuevas = [
        Entrada(sector_id=data.sector_id, estado=EstadoEntrada.DISPONIBLE.value)
        for _ in range(data.cantidad)
    ]
    db.add_all(nuevas)
    db.commit()
    return nuevas


def obtener_entradas(db: Session, skip: int = 0, limit: int = 100) -> list[Entrada]:
    return list(db.scalars(select(Entrada).order_by(Entrada.id).offset(skip).limit(limit)))


def obtener_entrada(db: Session, entrada_id: int) -> Entrada:
    """Devuelve la entrada o lanza RecursoNoEncontradoError."""
    entrada = db.get(Entrada, entrada_id)
    if entrada is None:
        raise RecursoNoEncontradoError(f"Entrada con id {entrada_id} no encontrada")
    return entrada


def actualizar_entrada(db: Session, entrada_id: int, data: EntradaUpdate) -> Entrada:
    """Alta/baja administrativa: solo alterna entre DISPONIBLE y ANULADA."""
    entrada = obtener_entrada(db, entrada_id)
    if entrada.estado in _ESTADOS_DE_PAGO:
        raise ConflictoError(
            "La entrada pertenece a una venta en curso o ya emitida y no puede modificarse manualmente"
        )
    if data.estado not in (EstadoEntrada.DISPONIBLE, EstadoEntrada.ANULADA):
        raise ReglaNegocioError(
            "Solo se puede cambiar una entrada a DISPONIBLE o ANULADA; "
            "RESERVADA y EMITIDA las gestiona el pago"
        )
    # Reactivar una entrada anulada vuelve a ocupar un lugar de la capacidad
    if entrada.estado == EstadoEntrada.ANULADA.value and data.estado == EstadoEntrada.DISPONIBLE:
        _validar_cupo(db, entrada.sector_id)
    entrada.estado = data.estado.value
    db.commit()
    db.refresh(entrada)
    return entrada


def eliminar_entrada(db: Session, entrada_id: int) -> None:
    entrada = obtener_entrada(db, entrada_id)
    if entrada.estado in _ESTADOS_DE_PAGO:
        raise ConflictoError("No se puede eliminar una entrada reservada o emitida")
    db.delete(entrada)
    db.commit()
