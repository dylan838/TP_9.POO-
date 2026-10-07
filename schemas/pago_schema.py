from decimal import Decimal

from pydantic import BaseModel, Field

from models.venta import EstadoVenta
from schemas.entrada_schema import EntradaResponse


class DatosTarjeta(BaseModel):
    """Datos de la tarjeta. Solo viajan a la pasarela: nunca se guardan."""

    numero: str = Field(
        ..., pattern=r"^\d{13,19}$", description="Solo dígitos, sin espacios",
        examples=["4111111111111111"],
    )
    titular: str = Field(..., min_length=1, max_length=100, examples=["JUAN PEREZ"])
    vencimiento: str = Field(..., pattern=r"^(0[1-9]|1[0-2])/\d{2}$", examples=["12/28"])
    cvv: str = Field(..., pattern=r"^\d{3,4}$", examples=["123"])


class PagoRequest(BaseModel):
    cliente_id: int = Field(..., examples=[1])
    entrada_ids: list[int] = Field(..., min_length=1, examples=[[1, 2]])
    tarjeta: DatosTarjeta


class PagoResponse(BaseModel):
    venta_id: int
    cliente_id: int
    estado: EstadoVenta
    total: Decimal
    referencia_pago: str
    entradas: list[EntradaResponse]
