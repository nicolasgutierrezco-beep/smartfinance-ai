"""Cálculo del límite de gasto diario (HU-04).

La idea en una frase: de lo que entra se descuenta lo que ya está comprometido
y lo que se quiere ahorrar, y el resto se reparte entre los días que faltan.
"""

from decimal import ROUND_FLOOR, Decimal

# Un mes nunca tiene menos de 28 días ni más de 31.
DIAS_MINIMOS_DEL_MES = 28
DIAS_MAXIMOS_DEL_MES = 31

# En Colombia no circulan centavos, así que el resultado va en pesos enteros.
SIN_CENTAVOS = Decimal("1")

CERO = Decimal("0")


class MontoInvalidoError(ValueError):
    """Se lanza cuando llega un monto en negativo."""


class MetaInalcanzableError(ValueError):
    """Se lanza cuando la meta de ahorro no cabe en lo que queda del mes."""


def _exigir_que_no_sea_negativo(monto: Decimal, nombre: str) -> None:
    """Corta de una vez si un monto viene en negativo."""
    if monto < CERO:
        raise MontoInvalidoError(
            f"El valor de {nombre} debe ser un monto numérico positivo"
        )


def _exigir_que_el_dia_exista(dias_del_mes: int, dia_actual: int) -> None:
    """Comprueba que el mes y el día sean posibles en un calendario real."""
    if not DIAS_MINIMOS_DEL_MES <= dias_del_mes <= DIAS_MAXIMOS_DEL_MES:
        raise ValueError(
            f"Un mes tiene entre {DIAS_MINIMOS_DEL_MES} y "
            f"{DIAS_MAXIMOS_DEL_MES} días"
        )
    if not 1 <= dia_actual <= dias_del_mes:
        raise ValueError("El día actual debe estar dentro del mes")


def _en_pesos(monto: Decimal) -> str:
    """Escribe 100000 como «100.000», que es como se lee un precio aquí."""
    return f"{monto:,.0f}".replace(",", ".")


def calcular_limite_diario(
    ingresos_mensuales: Decimal,
    gastos_fijos: Decimal,
    meta_ahorro: Decimal,
    dias_del_mes: int,
    dia_actual: int = 1,
    gastado_hasta_hoy: Decimal = Decimal("0"),
) -> Decimal:
    """Dice cuánto se puede gastar hoy y cada día que queda del mes."""
    _exigir_que_no_sea_negativo(ingresos_mensuales, "los ingresos")
    _exigir_que_no_sea_negativo(gastos_fijos, "los gastos fijos")
    _exigir_que_no_sea_negativo(meta_ahorro, "la meta")
    _exigir_que_no_sea_negativo(gastado_hasta_hoy, "lo gastado")
    _exigir_que_el_dia_exista(dias_del_mes, dia_actual)

    # Paso 1: lo que de verdad queda después de pagar lo obligatorio.
    disponible_del_mes = ingresos_mensuales - gastos_fijos
    if meta_ahorro > disponible_del_mes:
        raise MetaInalcanzableError(
            "La meta supera tu disponibilidad mensual "
            f"(${_en_pesos(disponible_del_mes)} COP máximo)"
        )

    # Paso 2: lo que sobra tras apartar el ahorro y descontar lo ya gastado.
    saldo_restante = max(
        CERO, disponible_del_mes - meta_ahorro - gastado_hasta_hoy
    )

    # Paso 3: repartirlo entre los días que faltan. Hoy todavía cuenta.
    dias_restantes = dias_del_mes - dia_actual + 1

    # Hacia abajo siempre: $9.166,67 se entrega como $9.166, nunca como $9.167.
    return (saldo_restante / dias_restantes).quantize(
        SIN_CENTAVOS, rounding=ROUND_FLOOR
    )
