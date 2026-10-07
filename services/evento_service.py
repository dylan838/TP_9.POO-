from sqlalchemy.orm import Session

from exceptions import ConflictoError, RecursoNoEncontradoError
from models.evento import Evento
from models.sector import Sector
from schemas.evento_schema import EventoCreate
from services import lugar_service


def _validar_lugar_existe(db: Session, lugar_id: int) -> None:
    if lugar_service.obtener_lugar_por_id(db, lugar_id) is None:
        raise RecursoNoEncontradoError(f"Lugar con id {lugar_id} no encontrado")


def crear_evento(db: Session, data: EventoCreate) -> Evento:
    _validar_lugar_existe(db, data.lugar_id)
    nuevo = Evento(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


def obtener_eventos(db: Session, skip: int = 0, limit: int = 100) -> list[Evento]:
    return db.query(Evento).offset(skip).limit(limit).all()


def obtener_evento(db: Session, evento_id: int) -> Evento:
    """Devuelve el evento o lanza RecursoNoEncontradoError."""
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if evento is None:
        raise RecursoNoEncontradoError(f"Evento con id {evento_id} no encontrado")
    return evento


def actualizar_evento(db: Session, evento_id: int, data: EventoCreate) -> Evento:
    evento = obtener_evento(db, evento_id)
    _validar_lugar_existe(db, data.lugar_id)
    for campo, valor in data.model_dump().items():
        setattr(evento, campo, valor)
    db.commit()
    db.refresh(evento)
    return evento


def eliminar_evento(db: Session, evento_id: int) -> None:
    evento = obtener_evento(db, evento_id)
    if db.query(Sector).filter(Sector.evento_id == evento_id).count() > 0:
        raise ConflictoError("No se puede eliminar el evento: tiene sectores asociados")
    db.delete(evento)
    db.commit()
