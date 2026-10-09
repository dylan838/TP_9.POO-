from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from exceptions import (
    EntradaYaUtilizadaError,
    TicketInvalidoError,
    TicketNoEmitidoError,
)
from models.entrada import Entrada, EstadoEntrada
from models.evento import Evento
from models.sector import Sector
from schemas.acceso_schema import AccesoRequest, AccesoResponse

MSG_INVALIDO = "Ticket Inválido o Inexistente"
MSG_YA_UTILIZADA = "Entrada ya utilizada"
MSG_NO_EMITIDO = "Ticket no emitido / Falta de pago"


def _buscar_entrada_por_qr(db: Session, codigo_qr: str) -> Entrada:
    entrada = db.scalar(select(Entrada).where(Entrada.codigo_qr == codigo_qr.strip()))
    if entrada is None:
        raise TicketInvalidoError(MSG_INVALIDO)
    return entrada


def _validar_puede_ingresar(entrada: Entrada) -> None:
    """Decide, según el estado, si la entrada habilita el ingreso."""
    estado = entrada.estado
    if estado == EstadoEntrada.EMITIDA.value:
        return
    if estado == EstadoEntrada.UTILIZADA.value:
        raise EntradaYaUtilizadaError(MSG_YA_UTILIZADA)
    if estado in (EstadoEntrada.DISPONIBLE.value, EstadoEntrada.RESERVADA.value):
        raise TicketNoEmitidoError(MSG_NO_EMITIDO)
    # ANULADA: la entrada fue dada de baja, equivale a un ticket sin validez
    raise TicketInvalidoError(MSG_INVALIDO)


def _registrar_ingreso(db: Session, entrada_id: int, momento: datetime) -> None:
    """Marca la entrada como UTILIZADA de forma atómica.

    El UPDATE solo actúa si la entrada sigue EMITIDA. Si dos acomodadores
    escanean el mismo QR a la vez, solo uno logra la actualización; el otro
    recibe "Entrada ya utilizada" y la hora del primero nunca se sobrescribe.
    """
    actualizadas = db.execute(
        update(Entrada)
        .where(Entrada.id == entrada_id, Entrada.estado == EstadoEntrada.EMITIDA.value)
        .values(estado=EstadoEntrada.UTILIZADA.value, fecha_ingreso=momento)
        .execution_options(synchronize_session=False)
    ).rowcount

    if actualizadas != 1:
        db.rollback()
        raise EntradaYaUtilizadaError(MSG_YA_UTILIZADA)

    db.commit()


def escanear_acceso(db: Session, datos: AccesoRequest) -> AccesoResponse:
    """HU 3: valida un QR en puerta y registra el ingreso."""
    entrada = _buscar_entrada_por_qr(db, datos.codigo_qr)
    _validar_puede_ingresar(entrada)

    entrada_id, sector_id = entrada.id, entrada.sector_id
    momento = datetime.now()
    _registrar_ingreso(db, entrada_id, momento)

    sector = db.get(Sector, sector_id)
    evento = db.get(Evento, sector.evento_id)
    return AccesoResponse(
        entrada_id=entrada_id,
        evento=evento.nombre,
        sector=sector.nombre,
        fecha_ingreso=momento,
    )
