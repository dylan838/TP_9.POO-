from sqlalchemy import func, select
from sqlalchemy.orm import Session

from exceptions import ConflictoError, ReglaNegocioError, RecursoNoEncontradoError
from models.entrada import Entrada, EstadoEntrada
from models.sector import Sector
from schemas.sector_schema import SectorCreate
from services import evento_service


def crear_sector(db: Session, data: SectorCreate) -> Sector:
    evento_service.obtener_evento(db, data.evento_id)  # valida que el evento exista
    nuevo = Sector(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


def obtener_sectores(db: Session, skip: int = 0, limit: int = 100) -> list[Sector]:
    return db.query(Sector).offset(skip).limit(limit).all()


def obtener_sector(db: Session, sector_id: int) -> Sector:
    """Devuelve el sector o lanza RecursoNoEncontradoError."""
    sector = db.query(Sector).filter(Sector.id == sector_id).first()
    if sector is None:
        raise RecursoNoEncontradoError(f"Sector con id {sector_id} no encontrado")
    return sector


def contar_entradas_vigentes(db: Session, sector_id: int) -> int:
    """Entradas que ocupan un lugar de la capacidad (todas menos las ANULADAS)."""
    return db.scalar(
        select(func.count(Entrada.id)).where(
            Entrada.sector_id == sector_id,
            Entrada.estado != EstadoEntrada.ANULADA.value,
        )
    )


def obtener_disponibilidad(db: Session, sector: Sector) -> int:
    """Entradas que se pueden comprar ahora: las que están DISPONIBLES.

    Única fuente de verdad: la usa la cotización (HU 1).
    """
    return db.scalar(
        select(func.count(Entrada.id)).where(
            Entrada.sector_id == sector.id,
            Entrada.estado == EstadoEntrada.DISPONIBLE.value,
        )
    )


def actualizar_sector(db: Session, sector_id: int, data: SectorCreate) -> Sector:
    sector = obtener_sector(db, sector_id)
    evento_service.obtener_evento(db, data.evento_id)
    vigentes = contar_entradas_vigentes(db, sector_id)
    if data.capacidad < vigentes:
        raise ReglaNegocioError(
            f"La capacidad no puede ser menor a las entradas ya generadas ({vigentes})"
        )
    for campo, valor in data.model_dump().items():
        setattr(sector, campo, valor)
    db.commit()
    db.refresh(sector)
    return sector


def eliminar_sector(db: Session, sector_id: int) -> None:
    sector = obtener_sector(db, sector_id)
    if db.query(Entrada).filter(Entrada.sector_id == sector_id).count() > 0:
        raise ConflictoError("No se puede eliminar el sector: tiene entradas asociadas")
    db.delete(sector)
    db.commit()
