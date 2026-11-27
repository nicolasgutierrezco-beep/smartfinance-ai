"""Pruebas de validar_fecha_vencimiento (HU-03)."""

from datetime import date

import pytest

from smartfinance.deudas import validar_fecha_vencimiento

HOY = date(2026, 11, 13)


@pytest.mark.parametrize(
    "fecha",
    [
        date(2026, 10, 10),  # fecha pasada, como en el escenario 2 de HU-03
        date(2026, 11, 12),  # ayer: el último día inválido
        date(2026, 11, 13),  # hoy: también es inválido (A-01)
    ],
)
def test_fecha_de_hoy_o_anterior_da_error(fecha):
    with pytest.raises(ValueError, match="posterior a la fecha actual"):
        validar_fecha_vencimiento(fecha, HOY)


@pytest.mark.parametrize(
    "fecha",
    [
        date(2026, 11, 14),  # mañana: el primer día válido
        date(2027, 1, 31),  # una fecha lejana
    ],
)
def test_fecha_futura_se_acepta(fecha):
    assert validar_fecha_vencimiento(fecha, HOY) is None