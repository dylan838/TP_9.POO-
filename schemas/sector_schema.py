from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SectorCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, examples=["Platea"])
    precio: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2, examples=["12000.00"])
    capacidad: int = Field(..., gt=0, examples=[100])
    evento_id: int = Field(..., gt=0, examples=[1])


class SectorResponse(BaseModel):
    id: int
    nombre: str
    precio: Decimal
    capacidad: int
    evento_id: int

    model_config = ConfigDict(from_attributes=True)
