from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from exceptions import (
    ConflictoError,
    PagoDenegadoError,
    RecursoNoEncontradoError,
    ReglaNegocioError,
)
from models.entrada import Entrada, EstadoEntrada
from models.sector import Sector
from models.venta import EstadoVenta, Venta
from schemas.entrada_schema import EntradaResponse
from schemas.pago_schema import PagoRequest, PagoResponse
from services import cliente_service
from services.pasarela_service import EstadoPasarela, PasarelaPago

MSG_NO_DISPONIBLES = "Los lugares seleccionados ya no se encuentran disponibles"


# ---------------------------------------------------------------- validaciones
def _validar_sin_repetidos(entrada_ids: list[int]) -> None:
    if len(set(entrada_ids)) != len(entrada_ids):
        raise ReglaNegocioError("La solicitud contiene entradas repetidas")


def _obtener_entradas(db: Session, entrada_ids: list[int]) -> list[Entrada]:
    entradas = list(
        db.scalars(select(Entrada).where(Entrada.id.in_(entrada_ids)).order_by(Entrada.id))
    )
    faltantes = sorted(set(entrada_ids) - {e.id for e in entradas})
    if faltantes:
        raise RecursoNoEncontradoError(f"Entradas inexistentes: {faltantes}")
    return entradas


def _validar_todas_disponibles(entradas: list[Entrada]) -> None:
    if any(e.estado != EstadoEntrada.DISPONIBLE.value for e in entradas):
        raise ConflictoError(MSG_NO_DISPONIBLES)


def _calcular_total(db: Session, entradas: list[Entrada]) -> Decimal:
    sector_ids = {e.sector_id for e in entradas}
    precios = {
        s.id: s.precio for s in db.scalars(select(Sector).where(Sector.id.in_(sector_ids)))
    }
    total = sum((precios[e.sector_id] for e in entradas), Decimal("0"))
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ------------------------------------------------------------- transacciones
def _reservar_entradas(db: Session, cliente_id: int, entrada_ids: list[int]) -> Venta:
    """TRANSACCIÓN 1: valida, crea la Venta PENDIENTE y reserva las entradas.

    Todo o nada: si algo falla, se hace rollback y no queda rastro.
    """
    _validar_sin_repetidos(entrada_ids)
    entradas = _obtener_entradas(db, entrada_ids)

    # Aborto temprano (Escenario 3): ni siquiera se crea la venta ni se llama a la pasarela
    _validar_todas_disponibles(entradas)

    venta = Venta(
        cliente_id=cliente_id,
        estado=EstadoVenta.PENDIENTE.value,
        total=_calcular_total(db, entradas),
    )
    db.add(venta)
    db.flush()  # obtiene venta.id sin cerrar la transacción

    # Reclamo ATÓMICO: un único UPDATE condicionado al estado actual. Si otro
    # usuario se llevó alguna entrada entre la validación y este punto, el
    # UPDATE no la toca y el conteo no coincide.
    reclamadas = db.execute(
        update(Entrada)
        .where(
            Entrada.id.in_(entrada_ids),
            Entrada.estado == EstadoEntrada.DISPONIBLE.value,
        )
        .values(estado=EstadoEntrada.RESERVADA.value, venta_id=venta.id)
        .execution_options(synchronize_session=False)
    ).rowcount

    if reclamadas != len(entrada_ids):
        db.rollback()  # deshace también la Venta recién insertada
        raise ConflictoError(MSG_NO_DISPONIBLES)

    db.commit()
    db.refresh(venta)
    return venta


def _confirmar_venta(db: Session, venta_id: int, referencia: str) -> PagoResponse:
    """TRANSACCIÓN 2 (pago aprobado): emite las entradas y marca la Venta PAGADA."""
    venta = db.get(Venta, venta_id)
    entradas = list(
        db.scalars(select(Entrada).where(Entrada.venta_id == venta_id).order_by(Entrada.id))
    )

    ahora = datetime.now()
    for entrada in entradas:
        entrada.estado = EstadoEntrada.EMITIDA.value
        entrada.fecha_emision = ahora
    venta.estado = EstadoVenta.PAGADA.value
    venta.referencia_pago = referencia

    db.commit()  # entradas + venta cambian juntas o no cambian

    return PagoResponse(
        venta_id=venta.id,
        cliente_id=venta.cliente_id,
        estado=venta.estado,
        total=venta.total,
        referencia_pago=referencia,
        entradas=[EntradaResponse.model_validate(e) for e in entradas],
    )


def _liberar_reserva(db: Session, venta_id: int) -> None:
    """TRANSACCIÓN 2 (pago rechazado o fallido): devuelve las entradas a DISPONIBLE."""
    db.execute(
        update(Entrada)
        .where(
            Entrada.venta_id == venta_id,
            Entrada.estado == EstadoEntrada.RESERVADA.value,
        )
        .values(estado=EstadoEntrada.DISPONIBLE.value, venta_id=None)
        .execution_options(synchronize_session=False)
    )
    venta = db.get(Venta, venta_id)
    venta.estado = EstadoVenta.CANCELADA.value
    db.commit()


# ------------------------------------------------------------------ caso de uso
def iniciar_pago(db: Session, datos: PagoRequest, pasarela: PasarelaPago) -> PagoResponse:
    """HU 2: reserva las entradas, cobra en la pasarela y emite (o libera)."""
    cliente = cliente_service.obtener_cliente(db, datos.cliente_id)

    venta = _reservar_entradas(db, cliente.id, datos.entrada_ids)
    venta_id, total = venta.id, venta.total

    # La pasarela se consulta FUERA de la transacción: no se mantiene un
    # bloqueo de base de datos durante una llamada de red.
    try:
        respuesta = pasarela.procesar_pago(total, datos.tarjeta)
    except Exception:
        _liberar_reserva(db, venta_id)  # si la pasarela falla, no se quedan retenidas
        raise

    if respuesta.estado != EstadoPasarela.APROBADO:
        _liberar_reserva(db, venta_id)
        raise PagoDenegadoError("Pago denegado")

    return _confirmar_venta(db, venta_id, respuesta.referencia)
