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


class GastosSuperanIngresosError(ValueError):
    """Se lanza cuando los gastos fijos son mayores que los ingresos del mes."""


def _como_monto(valor: object, nombre: str) -> Decimal:
    """Acepta Decimal o int y lo devuelve como Decimal; rechaza float y bool.

    Un float guarda la plata con error (0.1 + 0.2 no da 0.3), así que no
    se deja entrar aunque "parezca" un número. Un bool es técnicamente un
    int en Python, pero nadie quiere que True valga $1.
    """
    if isinstance(valor, bool) or not isinstance(valor, (Decimal, int)):
        raise MontoInvalidoError(
            f"El valor de {nombre} llegó como {type(valor).__name__}; "
            "debe ser Decimal (o un entero), nunca float, para no perder "
            "centavos"
        )
    return Decimal(valor)


def _como_dia(valor: object, nombre: str) -> int:
    """Acepta solo enteros de verdad para los días; rechaza bool y float."""
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValueError(
            f"El valor de {nombre} debe ser un número entero de días, "
            f"no {type(valor).__name__}"
        )
    return valor


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
    # Primero el tipo, luego el valor: así un float o un bool se rechazan con
    # un mensaje propio y no con un TypeError de Python a mitad de la cuenta.
    ingresos_mensuales = _como_monto(ingresos_mensuales, "los ingresos")
    gastos_fijos = _como_monto(gastos_fijos, "los gastos fijos")
    meta_ahorro = _como_monto(meta_ahorro, "la meta")
    gastado_hasta_hoy = _como_monto(gastado_hasta_hoy, "lo gastado")
    dias_del_mes = _como_dia(dias_del_mes, "los días del mes")
    dia_actual = _como_dia(dia_actual, "el día actual")

    _exigir_que_no_sea_negativo(ingresos_mensuales, "los ingresos")
    _exigir_que_no_sea_negativo(gastos_fijos, "los gastos fijos")
    _exigir_que_no_sea_negativo(meta_ahorro, "la meta")
    _exigir_que_no_sea_negativo(gastado_hasta_hoy, "lo gastado")
    _exigir_que_el_dia_exista(dias_del_mes, dia_actual)

    # Paso 1: lo que de verdad queda después de pagar lo obligatorio.
    disponible_del_mes = ingresos_mensuales - gastos_fijos
    if disponible_del_mes < CERO:
        # Si lo obligatorio ya supera lo que entra, no hay nada que repartir
        # ni que ahorrar. Se avisa con las dos cifras, sin «máximos» negativos.
        raise GastosSuperanIngresosError(
            f"Tus gastos fijos (${_en_pesos(gastos_fijos)} COP) superan tus "
            f"ingresos (${_en_pesos(ingresos_mensuales)} COP): este mes no hay "
            "disponibilidad para ahorrar"
        )
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
