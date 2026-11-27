"""Pruebas de evaluar_gasto_ocio (HU-02). Tope de ocio: 100.000."""

import pytest

from smartfinance.recomendaciones import evaluar_gasto_ocio

TOPE = 100000

def gastos(ocio, cantidad):
    """Arma una lista con un gasto de ocio y el resto en comida."""
    lista = [{"concepto": "Cine", "monto": ocio, "categoria": "Ocio"}]
    for _ in range(cantidad - 1):
        lista.append({"concepto": "Mercado", "monto": 1000, "categoria": "Comida"})
    return lista

@pytest.mark.parametrize(
    "ocio, esperado",
    [
        (99999, 0),  # R2: un peso por debajo del tope
        (100000, 0),  # R2: igual al tope no es superarlo (A-05)
        (100001, 1),  # R3: un peso por encima
        (120000, 20000),  # R3: escenario 1 de HU-02 (A-04)
        (100000.50, 0.50),  # R3: con centavos
    ],
)
def test_tabla_de_decision(ocio, esperado):
    assert evaluar_gasto_ocio(gastos(ocio, 5), TOPE) == pytest.approx(esperado)


@pytest.mark.parametrize(
    "cantidad",
    [
        2,  # R1: escenario 2 de HU-02, usuario nuevo
        4,  # R1: último valor sin historial suficiente
    ],
)
def test_pocas_transacciones_da_error(cantidad):
    with pytest.raises(ValueError, match="al menos 5 transacciones"):
        evaluar_gasto_ocio(gastos(120000, cantidad), TOPE)

def test_lista_vacia_da_error():
    with pytest.raises(ValueError, match="al menos 5 transacciones"):
        evaluar_gasto_ocio([], TOPE)

def test_con_los_gastos_del_mes(gastos_del_mes):
    # 121.900 de ocio menos el tope de 100.000
    assert evaluar_gasto_ocio(gastos_del_mes, TOPE) == pytest.approx(21900)