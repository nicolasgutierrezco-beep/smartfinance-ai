"""Valores limite de calcular_limite_diario (HU-04) que faltaban en la semana 5."""

from decimal import Decimal

import pytest

from smartfinance.presupuesto import (
    GastosSuperanIngresosError,
    MetaInalcanzableError,
    calcular_limite_diario,
)

INGRESOS = Decimal("3000000")


@pytest.mark.parametrize(
    "dias, esperado",
    [
        (28, Decimal("107142")),  # febrero: el primer valor valido
        (31, Decimal("96774")),  # mes de 31 dias: el ultimo valor valido
    ],
)
def test_meses_validos(dias, esperado):
    resultado = calcular_limite_diario(INGRESOS, Decimal("0"), Decimal("0"), dias)
    assert resultado == esperado


@pytest.mark.parametrize("dias", [27, 32])  # justo por fuera del rango de 28 a 31
def test_meses_invalidos_dan_error(dias):
    with pytest.raises(ValueError):
        calcular_limite_diario(INGRESOS, Decimal("0"), Decimal("0"), dias)


def test_meta_un_peso_mayor_que_lo_disponible():
    with pytest.raises(MetaInalcanzableError):
        calcular_limite_diario(INGRESOS, Decimal("0"), Decimal("3000001"), 30)


def test_gastos_fijos_un_peso_mayores_que_los_ingresos():
    with pytest.raises(GastosSuperanIngresosError):
        calcular_limite_diario(INGRESOS, Decimal("3000001"), Decimal("0"), 30)