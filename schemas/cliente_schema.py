from pydantic import BaseModel, ConfigDict, Field

_PATRON_EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class ClienteCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=150, examples=["Juan Pérez"])
    email: str = Field(..., pattern=_PATRON_EMAIL, examples=["juan@mail.com"])


class ClienteResponse(BaseModel):
    id: int
    nombre: str
    email: str

    model_config = ConfigDict(from_attributes=True)
