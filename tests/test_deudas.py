"""Pruebas de deudas.py (HU-03 y HU-06). BORRADOR GENERADO POR IA, SIN REVISAR."""

from datetime import date
from decimal import Decimal

import pytest

from smartfinance.deudas import (
    Deuda,
    DeudaYaPagadaError,
    EstadoDeuda,
    FechaVencimientoInvalidaError,
    generar_alerta_vencimiento,
    marcar_como_pagada,
    total_pendiente,
    validar_fecha_vencimiento,
)

HOY = date(2026, 11, 13)


@pytest.mark.parametrize(
    "fecha",
    [
        date(2026, 10, 10),  # fecha pasada (HU-03 escenario 2)
        date(2026, 11, 12),  # ayer
    ],
)
def test_fecha_pasada_lanza_error(fecha):
    with pytest.raises(FechaVencimientoInvalidaError):
        validar_fecha_vencimiento(fecha, HOY)


def test_fecha_hoy_es_valida():
    # Vencer hoy no es una fecha pasada.
    validar_fecha_vencimiento(HOY, HOY)


def test_fecha_futura_es_valida():
    validar_fecha_vencimiento(date(2026, 11, 20), HOY)


def test_alerta_dos_dias_antes():
    deuda = Deuda("tarjeta de crédito", Decimal("200000"), date(2026, 11, 15))
    assert generar_alerta_vencimiento(deuda, HOY) is not None


@pytest.mark.parametrize(
    "fecha",
    [
        date(2026, 11, 20),  # faltan 7 días
        date(2026, 11, 16),  # faltan 3 días
    ],
)
def test_sin_alerta_si_falta_mucho(fecha):
    deuda = Deuda("tarjeta de crédito", Decimal("200000"), fecha)
    assert generar_alerta_vencimiento(deuda, HOY) is None


def test_deuda_pagada_no_genera_alerta():
    deuda = Deuda("tarjeta de crédito", Decimal("200000"), date(2026, 11, 15),
                  EstadoDeuda.PAGADO)
    assert generar_alerta_vencimiento(deuda, HOY) is None


def test_marcar_como_pagada_devuelve_deuda():
    deuda = Deuda("servicio de Internet", Decimal("80000"), date(2026, 11, 20))
    assert isinstance(marcar_como_pagada(deuda), Deuda)


def test_pagar_dos_veces_lanza_error():
    deuda = Deuda("servicio de Internet", Decimal("80000"), date(2026, 11, 20),
                  EstadoDeuda.PAGADO)
    with pytest.raises(DeudaYaPagadaError):
        marcar_como_pagada(deuda)


def test_total_pendiente(deudas_sinteticas):
    esperado = sum(
        d.monto_total for d in deudas_sinteticas
        if d.estado is EstadoDeuda.PENDIENTE
    )
    assert total_pendiente(deudas_sinteticas) == esperado


def test_deuda_con_monto_cero_lanza_error():
    # HU-07: el valor debe ser un monto numérico positivo.
    with pytest.raises(ValueError):
        Deuda("cuota de la natillera", Decimal("0"), date(2026, 11, 30))
