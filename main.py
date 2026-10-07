from fastapi import FastAPI

from database import Base, engine
from models import lugar  # noqa: F401  (registra el modelo en Base.metadata)
from routers import lugar_router

# Crea las tablas si no existen (para producción conviene usar Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SmartTicket API",
    description="Backend del sistema SmartTicket",
    version="0.1.0",
)

app.include_router(lugar_router.router)


@app.get("/", tags=["Root"])
def root():
    return {"mensaje": "SmartTicket API funcionando"}
