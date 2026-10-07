from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from exceptions import (
    ConflictoError,
    PagoDenegadoError,
    RecursoNoEncontradoError,
    ReglaNegocioError,
)


def registrar_manejadores(app: FastAPI) -> None:
    """Traduce las excepciones de dominio a respuestas HTTP."""

    @app.exception_handler(RecursoNoEncontradoError)
    async def no_encontrado(request: Request, exc: RecursoNoEncontradoError):
        return JSONResponse(status_code=404, content={"detail": exc.mensaje})

    @app.exception_handler(ConflictoError)
    async def conflicto(request: Request, exc: ConflictoError):
        return JSONResponse(status_code=409, content={"detail": exc.mensaje})

    @app.exception_handler(PagoDenegadoError)
    async def pago_denegado(request: Request, exc: PagoDenegadoError):
        return JSONResponse(status_code=402, content={"detail": exc.mensaje})

    # Cubre también CantidadInvalidaError y CapacidadInsuficienteError (subclases)
    @app.exception_handler(ReglaNegocioError)
    async def regla_negocio(request: Request, exc: ReglaNegocioError):
        return JSONResponse(status_code=400, content={"detail": exc.mensaje})
