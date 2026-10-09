from datetime import datetime

from pydantic import BaseModel, Field


class AccesoRequest(BaseModel):
    codigo_qr: str = Field(..., min_length=1, max_length=100, examples=["3f9a1c0e5b7d4a6e8c2b9d1f0a4e7c63"])


class AccesoResponse(BaseModel):
    mensaje: str = "Acceso Permitido"
    entrada_id: int
    evento: str
    sector: str
    fecha_ingreso: datetime
