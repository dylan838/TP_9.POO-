from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EventoCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=150, examples=["Concierto de Rock"])
    fecha: datetime = Field(..., examples=["2026-12-15T21:00:00"])
    lugar_id: int = Field(..., gt=0, examples=[1])


class EventoResponse(BaseModel):
    id: int
    nombre: str
    fecha: datetime
    lugar_id: int

    model_config = ConfigDict(from_attributes=True)
