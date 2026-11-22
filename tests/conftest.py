"""Datos de prueba sintéticos compartidos por las pruebas.

Origen: generados con IA (Claude) y revisados a mano. Son gastos y deudas de una
persona inventada que vive en Neiva. No hay nombres, cédulas, teléfonos ni
cuentas de personas reales, y los negocios mencionados son inventados.

Casos difíciles incluidos a propósito: tildes y ñ, apóstrofo, texto vacío,
espacios sobrantes, monto en cero y montos con centavos.
"""

from datetime import date
from decimal import Decimal

import pytest

from smartfinance.deudas import Deuda, EstadoDeuda
from smartfinance.recomendaciones import Transaccion


@pytest.fixture
def transacciones_sinteticas() -> list[Transaccion]:
    """Nueve gastos de un mes. Ocio suma $121.900; el resto, $69.000."""
    return [
        Transaccion("Almuerzo corriente en el centro de Neiva", Decimal("15000"),
                    "Alimentación"),
        Transaccion("Achiras y bizcochos en el terminal", Decimal("8000"),
                    "Alimentación"),
        # Tildes y ñ en el concepto.
        Transaccion("Piñata y torta para el cumpleaños de la sobrina",
                    Decimal("45000"), "Ocio"),
        Transaccion("Entrada a cine con crispetas", Decimal("32000"), "Ocio"),
        Transaccion("Suscripción de streaming", Decimal("26900"), "Ocio"),
        # Apóstrofo en el nombre de un negocio inventado.
        Transaccion("Tejo con los compañeros en D'Alirio", Decimal("18000"),
                    "Ocio"),
        # Texto vacío: el concepto no afecta la cuenta.
        Transaccion("", Decimal("5000"), "Transporte"),
        # Monto en cero: un mototaxi que no cobró.
        Transaccion("Mototaxi al barrio, cortesía", Decimal("0"), "Transporte"),
        Transaccion("Mercado de la semana", Decimal("41000"), "Alimentación"),
    ]


@pytest.fixture
def deudas_sinteticas() -> list[Deuda]:
    """Cinco deudas de noviembre de 2026. Las pendientes suman $630.000."""
    return [
        Deuda("tarjeta de crédito", Decimal("200000"), date(2026, 11, 15)),
        Deuda("servicio de Internet", Decimal("80000"), date(2026, 11, 20)),
        # Ñ y espacios sobrantes que el constructor debe recortar.
        Deuda("  cuota de la moto en la Cooperativa Ñambú  ", Decimal("350000"),
              date(2026, 11, 28)),
        # Apóstrofo, y ya pagada: no suma al total.
        Deuda("fiado en la tienda D'Toño", Decimal("45000"), date(2026, 11, 10),
              EstadoDeuda.PAGADO),
        # Monto en cero: la cuota de la natillera ya se abonó completa.
        Deuda("cuota de la natillera", Decimal("0"), date(2026, 11, 30)),
    ]
