from sqlalchemy import select
from sqlalchemy.orm import Session

from exceptions import ConflictoError, RecursoNoEncontradoError
from models.cliente import Cliente
from schemas.cliente_schema import ClienteCreate


def crear_cliente(db: Session, data: ClienteCreate) -> Cliente:
    existente = db.scalar(select(Cliente).where(Cliente.email == data.email))
    if existente is not None:
        raise ConflictoError("Ya existe un cliente con ese email")
    nuevo = Cliente(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


def obtener_clientes(db: Session, skip: int = 0, limit: int = 100) -> list[Cliente]:
    return list(db.scalars(select(Cliente).offset(skip).limit(limit)))


def obtener_cliente(db: Session, cliente_id: int) -> Cliente:
    """Devuelve el cliente o lanza RecursoNoEncontradoError."""
    cliente = db.get(Cliente, cliente_id)
    if cliente is None:
        raise RecursoNoEncontradoError(f"Cliente con id {cliente_id} no encontrado")
    return cliente
