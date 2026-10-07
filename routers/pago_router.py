from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.pago_schema import PagoRequest, PagoResponse
from services import pago_service
from services.pasarela_service import PasarelaPago, get_pasarela

router = APIRouter(tags=["Pagos"])


@router.post(
    "/iniciar-pago/",
    response_model=PagoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Pagar entradas con tarjeta",
    description=(
        "Reserva las entradas indicadas, procesa el pago en la pasarela y, si es aprobado, "
        "crea la venta como `PAGADA` y emite las entradas con su código QR. "
        "Para probar un rechazo use la tarjeta `4000000000000002`."
    ),
    responses={
        402: {"description": "Pago denegado por la pasarela"},
        404: {"description": "El cliente o alguna entrada no existen"},
        409: {"description": "Los lugares seleccionados ya no se encuentran disponibles"},
    },
)
def iniciar_pago(
    datos: PagoRequest,
    db: Session = Depends(get_db),
    pasarela: PasarelaPago = Depends(get_pasarela),
):
    return pago_service.iniciar_pago(db, datos, pasarela)
