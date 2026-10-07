from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.cotizacion_schema import CotizacionRequest, CotizacionResponse
from services import cotizacion_service

router = APIRouter(prefix="/cotizaciones", tags=["Cotizaciones"])


@router.post(
    "/",
    response_model=CotizacionResponse,
    status_code=status.HTTP_200_OK,
    summary="Cotizar una compra de entradas",
    description=(
        "Calcula el costo total exacto de comprar `cantidad` entradas de un sector "
        "de un evento, sin reservar ni cobrar nada."
    ),
    responses={
        400: {"description": "Cantidad inválida o capacidad insuficiente"},
        404: {"description": "El evento o el sector no existen"},
    },
)
def cotizar(datos: CotizacionRequest, db: Session = Depends(get_db)):
    return cotizacion_service.cotizar(db, datos)
