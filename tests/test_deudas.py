"""Pruebas de deudas.py: vencimientos (HU-03) y pagos (HU-06).

Los esperados salen de las reglas escritas en registro_pruebas.md, sección 1,
nunca de ejecutar el código. Generadas con IA y revisadas una por una.
"""

from datetime import date, datetime
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
from smartfinance.presupuesto import MontoInvalidoError

HOY = date(2026, 11, 13)  # El «hoy» del escenario 1 de HU-03.

# ---------------------------------------------------------------------------
# validar_fecha_vencimiento: «debe ser posterior a la fecha actual»
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("fecha", "hoy"),
    [
        # Partición «pasada»: el escenario 2 de HU-03 tal cual.
        (date(2026, 10, 10), date(2026, 11, 2)),
        # Límite: ayer, el último día de la partición «pasada».
        (date(2026, 11, 12), HOY),
        # Límite: hoy. «Posterior» es estricto (ambigüedad A-01).
        (HOY, HOY),
    ],
    ids=["escenario-HU03", "ayer", "hoy"],
)
def test_fecha_no_posterior_a_hoy_se_rechaza(fecha, hoy):
    with pytest.raises(
        FechaVencimientoInvalidaError,
        match="^La fecha de vencimiento debe ser posterior a la fecha actual$",
    ):
        validar_fecha_vencimiento(fecha, hoy)


@pytest.mark.parametrize(
    "fecha",
    [
        date(2026, 11, 14),  # Límite: mañana, el primer día válido.
        date(2027, 11, 13),  # Partición «futura»: un año después.
    ],
    ids=["manana", "dentro-de-un-anio"],
)
def test_fecha_posterior_a_hoy_se_acepta(fecha):
    assert validar_fecha_vencimiento(fecha, HOY) is None


@pytest.mark.parametrize(
    "fecha",
    [
        "2026-11-15",  # Texto con forma de fecha.
        datetime(2026, 11, 15, 8, 0),  # Fecha con hora: date pero no solo date.
        None,  # Nada.
    ],
    ids=["texto", "datetime", "none"],
)
def test_fecha_de_tipo_invalido_lanza_type_error(fecha):
    with pytest.raises(TypeError):
        validar_fecha_vencimiento(fecha, HOY)


# ---------------------------------------------------------------------------
# generar_alerta_vencimiento: tabla de decisión (estado × días que faltan)
# ---------------------------------------------------------------------------

MENSAJE_BASE = "Recordatorio: tu tarjeta de crédito por $200.000 COP "


@pytest.mark.parametrize(
    ("estado", "vence", "esperado"),
    [
        # R1: pendiente y faltan 3 días: todavía no toca (primer día fuera).
        (EstadoDeuda.PENDIENTE, date(2026, 11, 16), None),
        # R2: pendiente y faltan 2: el escenario 1 de HU-03, texto exacto.
        (EstadoDeuda.PENDIENTE, date(2026, 11, 15), MENSAJE_BASE + "vence en 2 días"),
        # R3: pendiente y falta 1: en singular (ambigüedad A-02).
        (EstadoDeuda.PENDIENTE, date(2026, 11, 14), MENSAJE_BASE + "vence en 1 día"),
        # R4: pendiente y vence hoy: último día de aviso (A-02).
        (EstadoDeuda.PENDIENTE, HOY, MENSAJE_BASE + "vence hoy"),
        # R5: pendiente y ya venció ayer: no es preventiva (A-03).
        (EstadoDeuda.PENDIENTE, date(2026, 11, 12), None),
        # R6: pagada: nunca alerta, aunque falten 2 días.
        (EstadoDeuda.PAGADO, date(2026, 11, 15), None),
    ],
    ids=["R1-faltan-3", "R2-faltan-2", "R3-falta-1", "R4-hoy", "R5-vencida",
         "R6-pagada"],
)
def test_alerta_segun_tabla_de_decision(estado, vence, esperado):
    deuda = Deuda("tarjeta de crédito", Decimal("200000"), vence, estado)

    assert generar_alerta_vencimiento(deuda, HOY) == esperado


def test_alerta_con_datos_sinteticos_recorta_espacios_y_conserva_la_enie(
    deudas_sinteticas,
):
    """La cuota de la moto vence el 28; el 26 faltan 2 días."""
    moto = deudas_sinteticas[2]

    assert generar_alerta_vencimiento(moto, date(2026, 11, 26)) == (
        "Recordatorio: tu cuota de la moto en la Cooperativa Ñambú por "
        "$350.000 COP vence en 2 días"
    )


# ---------------------------------------------------------------------------
# Deuda: datos que no se pueden registrar
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("acreedor", ["", "   "], ids=["vacio", "solo-espacios"])
def test_acreedor_vacio_se_rechaza(acreedor):
    with pytest.raises(ValueError, match="acreedor"):
        Deuda(acreedor, Decimal("80000"), date(2026, 11, 20))


@pytest.mark.parametrize(
    "monto",
    [Decimal("-1"), 80000.0],
    ids=["negativo", "float"],
)
def test_monto_de_deuda_invalido_lanza_monto_invalido(monto):
    with pytest.raises(MontoInvalidoError):
        Deuda("servicio de Internet", monto, date(2026, 11, 20))


def test_deuda_en_cero_es_valida():
    """Límite: cero no es negativo (ambigüedad A-07)."""
    deuda = Deuda("cuota de la natillera", Decimal("0"), date(2026, 11, 30))

    assert deuda.monto_total == Decimal("0")


# ---------------------------------------------------------------------------
# marcar_como_pagada y total_pendiente (HU-06)
# ---------------------------------------------------------------------------


def test_marcar_como_pagada_cambia_solo_el_estado():
    """HU-06, escenario 1: «Servicio de Internet» por $80.000 pasa a Pagado."""
    deuda = Deuda("servicio de Internet", Decimal("80000"), date(2026, 11, 20))

    pagada = marcar_como_pagada(deuda)

    assert pagada.estado is EstadoDeuda.PAGADO
    assert pagada.acreedor == "servicio de Internet"
    assert pagada.monto_total == Decimal("80000")
    assert deuda.estado is EstadoDeuda.PENDIENTE  # La original no cambia.


def test_pagar_dos_veces_lanza_deuda_ya_pagada():
    """HU-06, escenario 2."""
    deuda = Deuda("servicio de Internet", Decimal("80000"), date(2026, 11, 20),
                  EstadoDeuda.PAGADO)

    with pytest.raises(
        DeudaYaPagadaError, match="^Esta deuda ya ha sido saldada previamente$"
    ):
        marcar_como_pagada(deuda)


def test_total_pendiente_suma_solo_las_pendientes(deudas_sinteticas):
    """200.000 + 80.000 + 350.000 + 0; la del fiado ya está pagada."""
    assert total_pendiente(deudas_sinteticas) == Decimal("630000")


def test_pagar_una_deuda_la_descuenta_del_total(deudas_sinteticas):
    """HU-06, escenario 1: el monto se descuenta del total de compromisos."""
    deudas_sinteticas[1] = marcar_como_pagada(deudas_sinteticas[1])

    assert total_pendiente(deudas_sinteticas) == Decimal("550000")


def test_total_pendiente_sin_deudas_es_cero():
    assert total_pendiente([]) == Decimal("0")
