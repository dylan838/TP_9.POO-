"""Excepciones de dominio.

Los servicios las lanzan sin saber nada de HTTP; la traducción a códigos
de estado se hace en un único lugar (exception_handlers.py).
"""


class DominioError(Exception):
    def __init__(self, mensaje: str):
        self.mensaje = mensaje
        super().__init__(mensaje)


class RecursoNoEncontradoError(DominioError):
    """El recurso solicitado no existe (-> 404)."""


class ConflictoError(DominioError):
    """La operación choca con el estado actual de los datos (-> 409)."""


class ReglaNegocioError(DominioError):
    """Se violó una regla de negocio (-> 400)."""


class CantidadInvalidaError(ReglaNegocioError):
    """La cantidad solicitada es cero o negativa."""


class CapacidadInsuficienteError(ReglaNegocioError):
    """No hay entradas disponibles suficientes en el sector."""


class PagoDenegadoError(DominioError):
    """La pasarela de pago rechazó la operación (-> 402)."""
