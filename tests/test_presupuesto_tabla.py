"""Particiones y límites de calcular_limite_diario. BORRADOR GENERADO POR IA."""

from decimal import Decimal

import pytest

from smartfinance.presupuesto import (
    MetaInalcanzableError,
    calcular_limite_diario,
)


@pytest.mark.parametrize(
    ("ingresos", "fijos", "meta", "dias", "esperado"),
    [
        (Decimal("1400000"), Decimal("0"), Decimal("0"), 28, Decimal("50000")),  # febrero
        (Decimal("3100000"), Decimal("0"), Decimal("0"), 31, Decimal("100000")),  # mes de 31
        (Decimal("1000000"), Decimal("400000"), Decimal("600000"), 30, Decimal("0")),  # meta = disponible
    ],
)
def test_limite_valido(ingresos, fijos, meta, dias, esperado):
    assert calcular_limite_diario(ingresos, fijos, meta, dias) == pytest.approx(esperado)


@pytest.mark.parametrize("dias", [27, 32])  # fuera del rango 28..31
def test_dias_fuera_de_rango(dias):
    with pytest.raises(ValueError):
        calcular_limite_diario(Decimal("1000000"), Decimal("0"), Decimal("0"), dias)


def test_meta_un_peso_mayor_que_disponible():
    with pytest.raises(MetaInalcanzableError):
        calcular_limite_diario(Decimal("1000000"), Decimal("400000"), Decimal("600001"), 30)
