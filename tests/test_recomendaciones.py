"""Pruebas de recomendaciones.py: recomendación por gasto en ocio (HU-02).

Es la función que combina condiciones; su tabla de decisión está en
registro_pruebas.md. Generadas con IA y revisadas una por una.
"""

from decimal import Decimal

import pytest

from smartfinance.presupuesto import MontoInvalidoError
from smartfinance.recomendaciones import (
    HistorialInsuficienteError,
    Transaccion,
    evaluar_gasto_ocio,
)

TOPE = Decimal("100000")
MENSAJE = (
    "Has superado tu límite de ocio; te recomendamos reducir ${} COP en "
    "suscripciones secundarias este mes"
)
HISTORIAL_INSUFICIENTE = (
    "^Se requieren al menos 5 transacciones registradas para generar "
    "sugerencias personalizadas$"
)


def _mes(ocio: Decimal, cantidad: int = 5) -> list[Transaccion]:
    """Un gasto de ocio por el monto dado y el resto en alimentación."""
    otras = [Transaccion("mercado", Decimal("1000"), "Alimentación")] * (cantidad - 1)
    return [Transaccion("cine", ocio, "Ocio"), *otras]


@pytest.mark.parametrize(
    ("cantidad", "ocio", "esperado"),
    [
        # R1: historial insuficiente, sin importar el ocio. Escenario 2 (2 trx).
        (2, Decimal("120000"), HistorialInsuficienteError),
        # R1, límite: 4 es el último valor de la partición insuficiente.
        (4, Decimal("120000"), HistorialInsuficienteError),
        # R2, límite: 5 es el primero suficiente; ocio por debajo, sin consejo.
        (5, Decimal("99999"), None),
        # R2, límite: igual al tope todavía no es «superar» (A-05).
        (5, Decimal("100000"), None),
        # R3, límite: un peso por encima ya genera la recomendación.
        (5, Decimal("100001"), MENSAJE.format("1")),
        # R3: escenario 1 de HU-02 con el exceso como monto (A-04).
        (5, Decimal("120000"), MENSAJE.format("20.000")),
    ],
    ids=["R1-2-trx", "R1-4-trx", "R2-debajo", "R2-igual", "R3-un-peso",
         "R3-escenario-HU02"],
)
def test_evaluar_gasto_ocio_segun_tabla_de_decision(cantidad, ocio, esperado):
    transacciones = _mes(ocio, cantidad)

    if esperado is HistorialInsuficienteError:
        with pytest.raises(HistorialInsuficienteError, match=HISTORIAL_INSUFICIENTE):
            evaluar_gasto_ocio(transacciones, TOPE)
    else:
        assert evaluar_gasto_ocio(transacciones, TOPE) == esperado


def test_sin_transacciones_es_historial_insuficiente():
    """Partición «lista vacía»: el usuario recién creado."""
    with pytest.raises(HistorialInsuficienteError, match=HISTORIAL_INSUFICIENTE):
        evaluar_gasto_ocio([], TOPE)


def test_el_tope_invalido_se_revisa_antes_que_el_historial():
    """R0: un tope negativo es error de datos aunque falten transacciones."""
    with pytest.raises(MontoInvalidoError):
        evaluar_gasto_ocio(_mes(Decimal("0"), cantidad=2), Decimal("-1"))


@pytest.mark.parametrize(
    ("ocio", "tope", "esperado"),
    [
        # Tope en cero y nada de ocio: no se superó nada.
        (Decimal("0"), Decimal("0"), None),
        # Centavos: $0,01 de exceso se pide como $1, nunca como $0.
        (Decimal("100000.01"), TOPE, MENSAJE.format("1")),
    ],
    ids=["tope-cero", "centavos"],
)
def test_bordes_del_monto(ocio, tope, esperado):
    assert evaluar_gasto_ocio(_mes(ocio), tope) == esperado


def test_solo_la_categoria_ocio_suma_para_el_tope():
    """Mucho gasto en otras categorías no dispara la recomendación de ocio.

    Tampoco «ocio» en minúscula: la normalización es tarea de HU-01 (A-06).
    """
    transacciones = [
        Transaccion("arriendo", Decimal("900000"), "Vivienda"),
        Transaccion("mercado", Decimal("300000"), "Alimentación"),
        Transaccion("cine", Decimal("150000"), "ocio"),
        Transaccion("bus", Decimal("2950"), "Transporte"),
        Transaccion("streaming", Decimal("26900"), "Ocio"),
    ]

    assert evaluar_gasto_ocio(transacciones, TOPE) is None


def test_con_datos_sinteticos_del_mes(transacciones_sinteticas):
    """Ocio: 45.000 + 32.000 + 26.900 + 18.000 = 121.900; exceso 21.900.

    Las 9 transacciones cuentan para el mínimo, incluidas la de concepto vacío
    y la de monto cero.
    """
    assert evaluar_gasto_ocio(transacciones_sinteticas, TOPE) == MENSAJE.format(
        "21.900"
    )


@pytest.mark.parametrize(
    "monto",
    [Decimal("-5000"), 5000.0, True],
    ids=["negativo", "float", "bool"],
)
def test_transaccion_con_monto_invalido_se_rechaza(monto):
    with pytest.raises(MontoInvalidoError):
        Transaccion("bus", monto, "Transporte")
