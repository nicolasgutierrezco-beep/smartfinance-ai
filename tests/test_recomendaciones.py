"""Pruebas de recomendaciones.py (HU-02). BORRADOR GENERADO POR IA, SIN REVISAR."""

from decimal import Decimal

import pytest

from smartfinance.recomendaciones import (
    HistorialInsuficienteError,
    Transaccion,
    evaluar_gasto_ocio,
)


def _transacciones(ocio, cantidad=5):
    """Una de ocio por el monto dado y el resto en alimentación."""
    otras = [Transaccion("mercado", Decimal("1000"), "Alimentación")] * (cantidad - 1)
    return [Transaccion("cine", ocio, "Ocio"), *otras]


def test_escenario_gherkin_recomienda_reducir():
    # HU-02 escenario 1: $120.000 en ocio con tope de $100.000.
    mensaje = evaluar_gasto_ocio(_transacciones(Decimal("120000")), Decimal("100000"))
    assert mensaje == (
        "Has superado tu límite de ocio; te recomendamos reducir $30.000 COP "
        "en suscripciones secundarias este mes"
    )


@pytest.mark.parametrize(
    "cantidad",
    [
        2,  # HU-02 escenario 2: usuario nuevo con 2 transacciones
        4,  # justo debajo del mínimo
    ],
)
def test_historial_insuficiente(cantidad):
    with pytest.raises(ValueError):
        evaluar_gasto_ocio(_transacciones(Decimal("120000"), cantidad), Decimal("100000"))


@pytest.mark.parametrize(
    ("ocio", "tope"),
    [
        (Decimal("50000"), Decimal("100000")),   # muy por debajo
        (Decimal("80000"), Decimal("100000")),   # por debajo
        (Decimal("99999"), Decimal("100000")),   # un peso por debajo
    ],
)
def test_sin_recomendacion_si_no_supera(ocio, tope):
    assert evaluar_gasto_ocio(_transacciones(ocio), tope) is None


def test_con_datos_sinteticos(transacciones_sinteticas):
    assert evaluar_gasto_ocio(transacciones_sinteticas, Decimal("100000"))
