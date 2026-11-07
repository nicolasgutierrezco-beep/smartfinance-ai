"""Cálculo del límite de gasto diario (HU-04).

La idea en una frase: de lo que entra se descuenta lo que ya está comprometido
y lo que se quiere ahorrar, y el resto se reparte entre los días que faltan.
"""

from decimal import ROUND_FLOOR, Decimal


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
    if ingresos_mensuales < 0:
        raise MontoInvalidoError(
            "El valor de los ingresos debe ser un monto numérico positivo"
        )
    if gastos_fijos < 0:
        raise MontoInvalidoError(
            "El valor de los gastos fijos debe ser un monto numérico positivo"
        )
    if meta_ahorro < 0:
        raise MontoInvalidoError(
            "El valor de la meta debe ser un monto numérico positivo"
        )
    if gastado_hasta_hoy < 0:
        raise MontoInvalidoError(
            "El valor de lo gastado debe ser un monto numérico positivo"
        )

    if dias_del_mes < 28 or dias_del_mes > 31:
        raise ValueError("Un mes tiene entre 28 y 31 días")
    if dia_actual < 1 or dia_actual > dias_del_mes:
        raise ValueError("El día actual debe estar dentro del mes")

    # Primer montón: lo que de verdad queda después de pagar lo obligatorio.
    disponible_del_mes = ingresos_mensuales - gastos_fijos

    if meta_ahorro > disponible_del_mes:
        maximo = "{:,.0f}".format(disponible_del_mes).replace(",", ".")
        raise MetaInalcanzableError(
            "La meta supera tu disponibilidad mensual ($" + maximo + " COP máximo)"
        )

    # Segundo montón: lo que sobra después de apartar el ahorro, menos lo ya gastado.
    saldo_restante = disponible_del_mes - meta_ahorro - gastado_hasta_hoy
    if saldo_restante < 0:
        saldo_restante = Decimal("0")

    # El día de hoy todavía cuenta, por eso se suma 1.
    dias_restantes = dias_del_mes - dia_actual + 1

    # Se redondea hacia abajo: si da $9.166,67 se devuelve $9.166, nunca $9.167.
    return (saldo_restante / dias_restantes).quantize(
        Decimal("1"), rounding=ROUND_FLOOR
    )
