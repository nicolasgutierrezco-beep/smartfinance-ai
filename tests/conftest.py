"""Datos de prueba inventados: los gastos de un mes de una persona en Neiva.

No todos son datos de personas reales. Los nombres de negocios son inventados."""

import pytest

def gasto(concepto, monto, categoria):
     return {"concepto": concepto, "monto": monto, "categoria": categoria}

@pytest.fixture
def gastos_del_mes():
    """Nueve gastos. Los de Ocio suman 45.000 + 32.000 + 26.900 + 18.000 = 121.900."""
    return [
        gasto("Almuerzo corriente en el centro", 15000, "Alimentacion"),
        gasto("Achiras en el terminal", 8000, "Alimentacion"),
        gasto("Piñata para el cumpleaños de la sobrina", 45000, "Ocio"),
        gasto("Cine con crispetas", 32000, "Ocio"),
        gasto("Suscripcion de streaming", 26900, "Ocio"),
        gasto("Tejo en D'Alirio", 18000, "Ocio"),
        gasto("", 5000, "Transporte"),
        gasto("Mototaxi de cortesia", 0, "Transporte"),
        gasto("Mercado de la semana", 41000, "Alimentacion"),
    ]