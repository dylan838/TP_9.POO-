from sqlalchemy.orm import Session

from models.lugar import Lugar
from schemas.lugar_schema import LugarCreate


def crear_lugar(db: Session, lugar_data: LugarCreate) -> Lugar:
    """Crea y persiste un nuevo lugar."""
    nuevo_lugar = Lugar(**lugar_data.model_dump())
    db.add(nuevo_lugar)
    db.commit()
    db.refresh(nuevo_lugar)
    return nuevo_lugar


def obtener_lugares(db: Session, skip: int = 0, limit: int = 100) -> list[Lugar]:
    """Devuelve todos los lugares, con paginación básica."""
    return db.query(Lugar).offset(skip).limit(limit).all()


def obtener_lugar_por_id(db: Session, lugar_id: int) -> Lugar | None:
    """Devuelve un lugar por su ID, o None si no existe."""
    return db.query(Lugar).filter(Lugar.id == lugar_id).first()

def actualizar_lugar(
    db: Session, lugar_id: int, lugar_data: LugarCreate
) -> Lugar | None:
    """Reemplaza los datos de un lugar. Devuelve None si no existe."""
    lugar = obtener_lugar_por_id(db, lugar_id)
    if lugar is None:
        return None

    for campo, valor in lugar_data.model_dump().items():
        setattr(lugar, campo, valor)

    db.commit()
    db.refresh(lugar)
    return lugar


def eliminar_lugar(db: Session, lugar_id: int) -> bool:
    """Elimina un lugar. Devuelve False si no existe."""
    lugar = obtener_lugar_por_id(db, lugar_id)
    if lugar is None:
        return False

    db.delete(lugar)
    db.commit()
    return True
