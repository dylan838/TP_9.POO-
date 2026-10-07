from fastapi import FastAPI

from database import Base, engine
from exception_handlers import registrar_manejadores
from models import cliente, entrada, evento, lugar, sector, venta  # noqa: F401
from routers import (
    cliente_router,
    cotizacion_router,
    entrada_router,
    evento_router,
    lugar_router,
    pago_router,
    sector_router,
)

# Crea las tablas si no existen (para producción conviene usar Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SmartTicket API",
    description="Backend del sistema SmartTicket",
    version="0.3.0",
)

registrar_manejadores(app)

app.include_router(lugar_router.router)
app.include_router(evento_router.router)
app.include_router(sector_router.router)
app.include_router(entrada_router.router)
app.include_router(cliente_router.router)
app.include_router(cotizacion_router.router)
app.include_router(pago_router.router)


@app.get("/", tags=["Root"])
def root():
    return {"mensaje": "SmartTicket API funcionando"}
