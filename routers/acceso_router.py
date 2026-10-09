from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.acceso_schema import AccesoRequest, AccesoResponse
from services import acceso_service

router = APIRouter(tags=["Acceso"])


@router.post(
    "/escanear-acceso/",
    response_model=AccesoResponse,
    status_code=status.HTTP_200_OK,
    summary="Escanear un QR en la puerta",
    description=(
        "Valida el código QR de una entrada. Si está `EMITIDA`, registra la hora de ingreso, "
        "la marca como `UTILIZADA` y responde `Acceso Permitido`."
    ),
    responses={
        400: {"description": "Ticket no emitido / Falta de pago"},
        404: {"description": "Ticket Inválido o Inexistente"},
        409: {"description": "Entrada ya utilizada"},
    },
)
def escanear_acceso(datos: AccesoRequest, db: Session = Depends(get_db)):
    return acceso_service.escanear_acceso(db, datos)
