"""Deudas y tarjetas: vencimientos (HU-03) y pagos (HU-06).

Todas las funciones reciben la fecha de hoy como dato y nunca leen el reloj del
sistema, igual que calcular_limite_diario: así las pruebas dan siempre lo mismo.
"""

from collections.abc import Iterable
from dataclasses import dataclass, replace
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from smartfinance.presupuesto import (
    CERO,
    _como_monto,
    _en_pesos,
    _exigir_que_no_sea_negativo,
)

# HU-03, escenario 1: la alerta sale cuando faltan 2 días para el vencimiento.
DIAS_DE_AVISO = 2


class EstadoDeuda(Enum):
    """Los dos estados que define el modelo de datos de la semana 4."""

    PENDIENTE = "Pendiente"
    PAGADO = "Pagado"


class FechaVencimientoInvalidaError(ValueError):
    """Se lanza cuando la fecha de vencimiento no es posterior a hoy."""


class DeudaYaPagadaError(ValueError):
    """Se lanza al intentar pagar una deuda que ya figura como pagada."""


def _como_fecha(valor: object, nombre: str) -> date:
    """Acepta solo date; rechaza datetime, texto y cualquier otro tipo.

    datetime es una subclase de date en Python, pero trae hora y no se puede
    restar de un date, así que se rechaza aquí con un mensaje propio.
    """
    if isinstance(valor, datetime) or not isinstance(valor, date):
        raise TypeError(
            f"{nombre} debe ser una fecha (date), no {type(valor).__name__}"
        )
    return valor


@dataclass(frozen=True)
class Deuda:
    """Una deuda del usuario, tal como la define el modelo de datos.

    Attributes:
        acreedor: A quién se le debe. No puede estar vacío; se guarda sin
            espacios sobrantes al inicio o al final.
        monto_total: Cuánto se debe, en pesos. Decimal o int, no negativo.
        fecha_vencimiento: Día en que vence.
        estado: Pendiente o Pagado. Por defecto Pendiente.

    Raises:
        ValueError: Si el acreedor está vacío o el estado no es un EstadoDeuda.
        MontoInvalidoError: Si el monto es negativo, float o bool.
        TypeError: Si la fecha no es un date.
    """

    acreedor: str
    monto_total: Decimal
    fecha_vencimiento: date
    estado: EstadoDeuda = EstadoDeuda.PENDIENTE

    def __post_init__(self) -> None:
        if not isinstance(self.acreedor, str) or not self.acreedor.strip():
            raise ValueError("El acreedor de la deuda no puede estar vacío")
        monto = _como_monto(self.monto_total, "el monto de la deuda")
        _exigir_que_no_sea_negativo(monto, "el monto de la deuda")
        _como_fecha(self.fecha_vencimiento, "La fecha de vencimiento")
        if not isinstance(self.estado, EstadoDeuda):
            raise ValueError("El estado debe ser Pendiente o Pagado")
        # La clase es inmutable; esta es la forma de normalizar en el constructor.
        object.__setattr__(self, "acreedor", self.acreedor.strip())
        object.__setattr__(self, "monto_total", monto)


def validar_fecha_vencimiento(fecha_vencimiento: date, hoy: date) -> None:
    """Comprueba que una deuda nueva venza después de hoy (HU-03, escenario 2).

    Args:
        fecha_vencimiento: Día en que vence la deuda que se quiere registrar.
        hoy: Fecha actual. Entra como dato para que el resultado sea repetible.

    Raises:
        FechaVencimientoInvalidaError: Si la fecha es hoy o ya pasó.
        TypeError: Si alguna de las dos no es un date.
    """
    fecha_vencimiento = _como_fecha(fecha_vencimiento, "La fecha de vencimiento")
    hoy = _como_fecha(hoy, "La fecha de hoy")
    # «Posterior» es estricto: una deuda que vence hoy tampoco se puede registrar.
    if fecha_vencimiento <= hoy:
        raise FechaVencimientoInvalidaError(
            "La fecha de vencimiento debe ser posterior a la fecha actual"
        )


def generar_alerta_vencimiento(deuda: Deuda, hoy: date) -> str | None:
    """Devuelve el recordatorio de la deuda si toca enviarlo hoy (HU-03).

    Toca enviarlo cuando la deuda está pendiente y faltan entre 0 y
    DIAS_DE_AVISO días para que venza. Una deuda pagada, una que ya venció o
    una que vence más adelante no generan alerta.

    Args:
        deuda: La deuda que revisa el agente en su verificación diaria.
        hoy: Fecha actual.

    Returns:
        El texto de la alerta, por ejemplo «Recordatorio: tu tarjeta de
        crédito por $200.000 COP vence en 2 días», o None si no toca.

    Raises:
        TypeError: Si deuda no es una Deuda o hoy no es un date.
    """
    if not isinstance(deuda, Deuda):
        raise TypeError(f"Se esperaba una Deuda, no {type(deuda).__name__}")
    hoy = _como_fecha(hoy, "La fecha de hoy")

    if deuda.estado is EstadoDeuda.PAGADO:
        return None
    dias_que_faltan = (deuda.fecha_vencimiento - hoy).days
    if not 0 <= dias_que_faltan <= DIAS_DE_AVISO:
        return None

    if dias_que_faltan == 0:
        cuando = "vence hoy"
    elif dias_que_faltan == 1:
        cuando = "vence en 1 día"
    else:
        cuando = f"vence en {dias_que_faltan} días"
    return (
        f"Recordatorio: tu {deuda.acreedor} por "
        f"${_en_pesos(deuda.monto_total)} COP {cuando}"
    )


def marcar_como_pagada(deuda: Deuda) -> Deuda:
    """Pasa una deuda de Pendiente a Pagado (HU-06).

    No modifica la deuda recibida: devuelve una copia con el estado nuevo.

    Args:
        deuda: La deuda que el usuario quiere marcar como pagada.

    Returns:
        Una Deuda igual a la recibida, con estado PAGADO.

    Raises:
        DeudaYaPagadaError: Si la deuda ya estaba pagada (HU-06, escenario 2).
        TypeError: Si no se recibe una Deuda.
    """
    if not isinstance(deuda, Deuda):
        raise TypeError(f"Se esperaba una Deuda, no {type(deuda).__name__}")
    if deuda.estado is EstadoDeuda.PAGADO:
        raise DeudaYaPagadaError("Esta deuda ya ha sido saldada previamente")
    return replace(deuda, estado=EstadoDeuda.PAGADO)


def total_pendiente(deudas: Iterable[Deuda]) -> Decimal:
    """Suma lo que falta por pagar: solo las deudas pendientes (HU-06).

    Args:
        deudas: Las deudas del usuario en el mes.

    Returns:
        La suma de monto_total de las deudas pendientes. Cero si no hay.
    """
    return sum(
        (d.monto_total for d in deudas if d.estado is EstadoDeuda.PENDIENTE),
        CERO,
    )
