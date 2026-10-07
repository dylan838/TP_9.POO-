from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.lugar_schema import LugarCreate, LugarResponse
from services import lugar_service

router = APIRouter(
    prefix="/lugares",
    tags=["Lugares"],
)


@router.post(
    "/",
    response_model=LugarResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un lugar",
    description="Registra un nuevo lugar (venue) en el sistema con su nombre y dirección.",
)
def crear_lugar(lugar: LugarCreate, db: Session = Depends(get_db)):
    return lugar_service.crear_lugar(db, lugar)


@router.get(
    "/",
    response_model=list[LugarResponse],
    summary="Listar todos los lugares",
    description="Devuelve la lista de lugares registrados. Admite paginación con `skip` y `limit`.",
)
def listar_lugares(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return lugar_service.obtener_lugares(db, skip=skip, limit=limit)


@router.get(
    "/{lugar_id}",
    response_model=LugarResponse,
    summary="Obtener un lugar por ID",
    description="Devuelve los datos de un lugar específico.",
    responses={404: {"description": "El lugar no existe"}},
)
def obtener_lugar(lugar_id: int, db: Session = Depends(get_db)):
    lugar = lugar_service.obtener_lugar_por_id(db, lugar_id)
    if lugar is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lugar con id {lugar_id} no encontrado",
        )
    return lugar
@router.put(
    "/{lugar_id}",
    response_model=LugarResponse,
    summary="Actualizar un lugar",
    description="Reemplaza el nombre y la dirección de un lugar existente.",
    responses={404: {"description": "El lugar no existe"}},
)
def actualizar_lugar(
    lugar_id: int, lugar: LugarCreate, db: Session = Depends(get_db)
):
    lugar_actualizado = lugar_service.actualizar_lugar(db, lugar_id, lugar)
    if lugar_actualizado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lugar con id {lugar_id} no encontrado",
        )
    return lugar_actualizado

@router.delete(
    "/{lugar_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un lugar",
    description="Elimina un lugar de forma permanente.",
    responses={404: {"description": "El lugar no existe"}},
)
def eliminar_lugar(lugar_id: int, db: Session = Depends(get_db)):
    if not lugar_service.eliminar_lugar(db, lugar_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lugar con id {lugar_id} no encontrado",
        )