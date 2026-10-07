from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.entrada_schema import (
    EntradaCreate,
    EntradaLoteCreate,
    EntradaResponse,
    EntradaUpdate,
)
from services import entrada_service

router = APIRouter(prefix="/entradas", tags=["Entradas"])


@router.post(
    "/",
    response_model=EntradaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generar una entrada",
    description="Genera una entrada `DISPONIBLE` en un sector, sin superar su capacidad.",
    responses={
        400: {"description": "Capacidad insuficiente"},
        404: {"description": "El sector no existe"},
    },
)
def crear_entrada(entrada: EntradaCreate, db: Session = Depends(get_db)):
    return entrada_service.crear_entrada(db, entrada)


@router.post(
    "/lote",
    response_model=list[EntradaResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Generar entradas en lote",
    description="Genera `cantidad` entradas `DISPONIBLES` en un sector, sin superar su capacidad.",
    responses={
        400: {"description": "Capacidad insuficiente"},
        404: {"description": "El sector no existe"},
    },
)
def crear_entradas_en_lote(lote: EntradaLoteCreate, db: Session = Depends(get_db)):
    return entrada_service.crear_entradas_en_lote(db, lote)


@router.get(
    "/",
    response_model=list[EntradaResponse],
    summary="Listar entradas",
    description="Devuelve las entradas registradas. Admite paginación con `skip` y `limit`.",
)
def listar_entradas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return entrada_service.obtener_entradas(db, skip=skip, limit=limit)


@router.get(
    "/{entrada_id}",
    response_model=EntradaResponse,
    summary="Obtener una entrada por ID",
    responses={404: {"description": "La entrada no existe"}},
)
def obtener_entrada(entrada_id: int, db: Session = Depends(get_db)):
    return entrada_service.obtener_entrada(db, entrada_id)


@router.put(
    "/{entrada_id}",
    response_model=EntradaResponse,
    summary="Anular o reactivar una entrada",
    description=(
        "Alterna una entrada entre `ANULADA` y `DISPONIBLE`. Las entradas `RESERVADA` y "
        "`EMITIDA` pertenecen a una venta y no se pueden modificar manualmente."
    ),
    responses={
        400: {"description": "Estado no permitido o capacidad insuficiente al reactivar"},
        404: {"description": "La entrada no existe"},
        409: {"description": "La entrada pertenece a una venta"},
    },
)
def actualizar_entrada(
    entrada_id: int, datos: EntradaUpdate, db: Session = Depends(get_db)
):
    return entrada_service.actualizar_entrada(db, entrada_id, datos)


@router.delete(
    "/{entrada_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una entrada",
    description="Solo se pueden eliminar entradas `DISPONIBLE` o `ANULADA`.",
    responses={
        404: {"description": "La entrada no existe"},
        409: {"description": "La entrada pertenece a una venta"},
    },
)
def eliminar_entrada(entrada_id: int, db: Session = Depends(get_db)):
    entrada_service.eliminar_entrada(db, entrada_id)
