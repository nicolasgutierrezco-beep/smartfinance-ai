"""Cálculo del límite de gasto diario (HU-04).

Todavía sin implementar: primero van las pruebas.
"""

from decimal import Decimal


class MontoInvalidoError(ValueError):
    """Se lanza cuando llega un monto en negativo."""


class MetaInalcanzableError(ValueError):
    """Se lanza cuando la meta de ahorro no cabe en lo que queda del mes."""


def calcular_limite_diario(
    ingresos_mensuales: Decimal,
    gastos_fijos: Decimal,
    meta_ahorro: Decimal,
    dias_del_mes: int,
    dia_actual: int = 1,
    gastado_hasta_hoy: Decimal = Decimal("0"),
) -> Decimal:
    """Dice cuánto se puede gastar hoy y cada día que queda del mes."""
    raise NotImplementedError("Pendiente: se implementa después de las pruebas.")
