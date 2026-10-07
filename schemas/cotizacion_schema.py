from decimal import Decimal

from pydantic import BaseModel, Field


class CotizacionRequest(BaseModel):
    evento_id: int = Field(..., examples=[1])
    sector_id: int = Field(..., examples=[1])
    # Sin gt=0 a propósito: si Pydantic validara esto devolvería 422.
    # La regla "cantidad inválida" (HTTP 400) vive en el servicio.
    cantidad: int = Field(..., examples=[2])


class CotizacionResponse(BaseModel):
    evento_id: int
    evento_nombre: str
    sector_id: int
    sector_nombre: str
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal
    total: Decimal
