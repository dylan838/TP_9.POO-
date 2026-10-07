from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.cliente_schema import ClienteCreate, ClienteResponse
from services import cliente_service

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post(
    "/",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un cliente",
    responses={409: {"description": "Ya existe un cliente con ese email"}},
)
def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    return cliente_service.crear_cliente(db, cliente)


@router.get("/", response_model=list[ClienteResponse], summary="Listar clientes")
def listar_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return cliente_service.obtener_clientes(db, skip=skip, limit=limit)


@router.get(
    "/{cliente_id}",
    response_model=ClienteResponse,
    summary="Obtener un cliente por ID",
    responses={404: {"description": "El cliente no existe"}},
)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return cliente_service.obtener_cliente(db, cliente_id)
