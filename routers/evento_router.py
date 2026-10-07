from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.evento_schema import EventoCreate, EventoResponse
from services import evento_service

router = APIRouter(prefix="/eventos", tags=["Eventos"])


@router.post(
    "/",
    response_model=EventoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un evento",
    description="Registra un evento asociado a un lugar existente.",
    responses={404: {"description": "El lugar indicado no existe"}},
)
def crear_evento(evento: EventoCreate, db: Session = Depends(get_db)):
    return evento_service.crear_evento(db, evento)


@router.get(
    "/",
    response_model=list[EventoResponse],
    summary="Listar eventos",
    description="Devuelve los eventos registrados. Admite paginación con `skip` y `limit`.",
)
def listar_eventos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return evento_service.obtener_eventos(db, skip=skip, limit=limit)


@router.get(
    "/{evento_id}",
    response_model=EventoResponse,
    summary="Obtener un evento por ID",
    responses={404: {"description": "El evento no existe"}},
)
def obtener_evento(evento_id: int, db: Session = Depends(get_db)):
    return evento_service.obtener_evento(db, evento_id)


@router.put(
    "/{evento_id}",
    response_model=EventoResponse,
    summary="Actualizar un evento",
    description="Reemplaza los datos de un evento existente.",
    responses={404: {"description": "El evento o el lugar no existen"}},
)
def actualizar_evento(
    evento_id: int, evento: EventoCreate, db: Session = Depends(get_db)
):
    return evento_service.actualizar_evento(db, evento_id, evento)


@router.delete(
    "/{evento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un evento",
    description="Elimina un evento. Falla con 409 si tiene sectores asociados.",
    responses={
        404: {"description": "El evento no existe"},
        409: {"description": "El evento tiene sectores asociados"},
    },
)
def eliminar_evento(evento_id: int, db: Session = Depends(get_db)):
    evento_service.eliminar_evento(db, evento_id)
