from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from models.venta import EstadoVenta


class VentaResponse(BaseModel):
    id: int
    cliente_id: int
    estado: EstadoVenta
    total: Decimal
    fecha: datetime
    referencia_pago: str | None = None

    model_config = ConfigDict(from_attributes=True)
