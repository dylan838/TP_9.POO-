"""Pasarela de pago simulada.

pago_service depende de la abstracción `PasarelaPago`, no de esta clase concreta:
para integrar una pasarela real (Mercado Pago, Stripe...) se escribe otra clase
con el mismo método y se cambia `get_pasarela`, sin tocar el servicio de pago.
"""
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Protocol
from uuid import uuid4

from schemas.pago_schema import DatosTarjeta


class EstadoPasarela(str, Enum):
    APROBADO = "Aprobado"
    RECHAZADO = "Rechazado"


@dataclass(frozen=True)
class RespuestaPasarela:
    estado: EstadoPasarela
    referencia: str | None = None


class PasarelaPago(Protocol):
    def procesar_pago(self, monto: Decimal, tarjeta: DatosTarjeta) -> RespuestaPasarela:
        ...


class PasarelaSimulada:
    """Aprueba todo salvo la tarjeta de prueba de rechazo."""

    TARJETA_RECHAZADA = "4000000000000002"

    def procesar_pago(self, monto: Decimal, tarjeta: DatosTarjeta) -> RespuestaPasarela:
        if tarjeta.numero == self.TARJETA_RECHAZADA:
            return RespuestaPasarela(EstadoPasarela.RECHAZADO)
        return RespuestaPasarela(
            EstadoPasarela.APROBADO, referencia=f"SIM-{uuid4().hex[:12].upper()}"
        )


def get_pasarela() -> PasarelaPago:
    """Dependencia de FastAPI (se puede reemplazar con dependency_overrides en tests)."""
    return PasarelaSimulada()
