from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.sector_schema import SectorCreate, SectorResponse
from services import sector_service

router = APIRouter(prefix="/sectores", tags=["Sectores"])


@router.post(
    "/",
    response_model=SectorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un sector",
    description="Registra un sector (con precio unitario y capacidad) dentro de un evento.",
    responses={404: {"description": "El evento indicado no existe"}},
)
def crear_sector(sector: SectorCreate, db: Session = Depends(get_db)):
    return sector_service.crear_sector(db, sector)


@router.get(
    "/",
    response_model=list[SectorResponse],
    summary="Listar sectores",
    description="Devuelve los sectores registrados. Admite paginación con `skip` y `limit`.",
)
def listar_sectores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return sector_service.obtener_sectores(db, skip=skip, limit=limit)


@router.get(
    "/{sector_id}",
    response_model=SectorResponse,
    summary="Obtener un sector por ID",
    responses={404: {"description": "El sector no existe"}},
)
def obtener_sector(sector_id: int, db: Session = Depends(get_db)):
    return sector_service.obtener_sector(db, sector_id)


@router.put(
    "/{sector_id}",
    response_model=SectorResponse,
    summary="Actualizar un sector",
    description="Reemplaza los datos de un sector. La capacidad no puede ser menor a las entradas ya emitidas.",
    responses={
        400: {"description": "Capacidad menor a las entradas emitidas"},
        404: {"description": "El sector o el evento no existen"},
    },
)
def actualizar_sector(
    sector_id: int, sector: SectorCreate, db: Session = Depends(get_db)
):
    return sector_service.actualizar_sector(db, sector_id, sector)


@router.delete(
    "/{sector_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un sector",
    description="Elimina un sector. Falla con 409 si tiene entradas asociadas.",
    responses={
        404: {"description": "El sector no existe"},
        409: {"description": "El sector tiene entradas asociadas"},
    },
)
def eliminar_sector(sector_id: int, db: Session = Depends(get_db)):
    sector_service.eliminar_sector(db, sector_id)
