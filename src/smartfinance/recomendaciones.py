"""Recomendación de ahorro por gasto en ocio (HU-02).

Esta es la parte de la regla que se puede decidir con cuentas: si hay historial
suficiente y si el gasto en ocio pasó el tope. Redactar consejos más elaborados
le tocará a la API del LLM (ADR-001); el monto a recortar lo calcula el código,
porque la plata no se estima.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import ROUND_CEILING, Decimal

from smartfinance.presupuesto import (
    CERO,
    SIN_CENTAVOS,
    _como_monto,
    _en_pesos,
    _exigir_que_no_sea_negativo,
)

# HU-02, escenario 2: con menos de 5 transacciones no hay sugerencias.
MINIMO_DE_TRANSACCIONES = 5

# La categoría que suma para el tope. La normaliza el clasificador de HU-01.
CATEGORIA_OCIO = "Ocio"


class HistorialInsuficienteError(ValueError):
    """Se lanza cuando hay menos transacciones de las necesarias."""


@dataclass(frozen=True)
class Transaccion:
    """Un gasto ya registrado y clasificado.

    Attributes:
        concepto: La frase original. Puede venir vacía: no afecta la cuenta.
        monto: Cuánto costó, en pesos. Decimal o int, no negativo.
        categoria: La categoría que le asignó el clasificador. No vacía.

    Raises:
        MontoInvalidoError: Si el monto es negativo, float o bool.
        ValueError: Si la categoría está vacía o el concepto no es texto.
    """

    concepto: str
    monto: Decimal
    categoria: str

    def __post_init__(self) -> None:
        if not isinstance(self.concepto, str):
            raise ValueError("El concepto debe ser texto")
        if not isinstance(self.categoria, str) or not self.categoria.strip():
            raise ValueError("La categoría de la transacción no puede estar vacía")
        monto = _como_monto(self.monto, "el monto de la transacción")
        _exigir_que_no_sea_negativo(monto, "el monto de la transacción")
        object.__setattr__(self, "monto", monto)


def evaluar_gasto_ocio(
    transacciones: Iterable[Transaccion], tope_ocio: Decimal
) -> str | None:
    """Dice si el usuario se pasó del tope de ocio y cuánto debería recortar.

    Combina dos condiciones, en este orden:
    1. ¿Hay al menos MINIMO_DE_TRANSACCIONES transacciones? Si no, error.
    2. ¿La suma de la categoría Ocio es mayor que el tope? Si no, no hay
       recomendación. Igual al tope todavía no es «superar».

    Args:
        transacciones: Las transacciones del mes. Todas cuentan para el mínimo;
            solo las de la categoría Ocio suman para el tope.
        tope_ocio: El tope mensual de ocio, en pesos. Puede ser cero.

    Returns:
        «Has superado tu límite de ocio; te recomendamos reducir $X COP en
        suscripciones secundarias este mes», donde X es el exceso redondeado
        hacia arriba al peso, o None si no hay exceso.

    Raises:
        MontoInvalidoError: Si el tope es negativo, float o bool.
        HistorialInsuficienteError: Si hay menos de 5 transacciones.
    """
    tope = _como_monto(tope_ocio, "el tope de ocio")
    _exigir_que_no_sea_negativo(tope, "el tope de ocio")

    transacciones = list(transacciones)
    if len(transacciones) < MINIMO_DE_TRANSACCIONES:
        raise HistorialInsuficienteError(
            f"Se requieren al menos {MINIMO_DE_TRANSACCIONES} transacciones "
            "registradas para generar sugerencias personalizadas"
        )

    gasto_ocio = sum(
        (t.monto for t in transacciones if t.categoria == CATEGORIA_OCIO), CERO
    )
    if gasto_ocio <= tope:
        return None

    # Hacia arriba: recortar $0,01 se pide como $1, nunca como $0.
    exceso = (gasto_ocio - tope).quantize(SIN_CENTAVOS, rounding=ROUND_CEILING)
    return (
        "Has superado tu límite de ocio; te recomendamos reducir "
        f"${_en_pesos(exceso)} COP en suscripciones secundarias este mes"
    )
