from pydantic import BaseModel, ConfigDict, Field


class LugarCreate(BaseModel):
    nombre: str = Field(
        ..., min_length=1, max_length=150, examples=["Teatro Colón"]
    )
    direccion: str = Field(
        ..., min_length=1, max_length=250, examples=["Cerrito 628, CABA"]
    )


class LugarResponse(BaseModel):
    id: int
    nombre: str
    direccion: str

    # Permite construir el esquema directamente desde un objeto SQLAlchemy
    model_config = ConfigDict(from_attributes=True)
