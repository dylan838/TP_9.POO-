from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from models.entrada import EstadoEntrada


class EntradaCreate(BaseModel):
    sector_id: int = Field(..., gt=0, examples=[1])


class EntradaLoteCreate(BaseModel):
    sector_id: int = Field(..., gt=0, examples=[1])
    cantidad: int = Field(..., gt=0, le=1000, examples=[10])


class EntradaUpdate(BaseModel):
    estado: EstadoEntrada = Field(..., examples=["ANULADA"])


class EntradaResponse(BaseModel):
    id: int
    sector_id: int
    venta_id: int | None = None
    estado: EstadoEntrada
    codigo_qr: str | None = None
    fecha_emision: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
