"""Particiones y valores límite de calcular_limite_diario (HU-04).

Completa las 15 pruebas de test_presupuesto.py, que no se tocaron. Aquí van solo
los bordes y particiones que esas pruebas no cubrían. Los esperados se calculan
a mano con la regla: (ingresos − fijos − meta − gastado) ÷ días que faltan.
"""

from decimal import Decimal

import pytest

from smartfinance.presupuesto import (
    GastosSuperanIngresosError,
    MetaInalcanzableError,
    MontoInvalidoError,
    calcular_limite_diario,
)

BASE = {
    "ingresos_mensuales": Decimal("3000000"),
    "gastos_fijos": Decimal("0"),
    "meta_ahorro": Decimal("0"),
    "dias_del_mes": 30,
}


@pytest.mark.parametrize(
    ("cambios", "esperado"),
    [
        # Límite dias_del_mes: 28 es el primer valor válido. 3.000.000 / 28.
        ({"dias_del_mes": 28}, Decimal("107142")),
        # Límite dias_del_mes: 31 es el último valor válido. 3.000.000 / 31.
        ({"dias_del_mes": 31}, Decimal("96774")),
        # Límite dia_actual: el día 1 reparte entre los 30 días.
        ({"dia_actual": 1}, Decimal("100000")),
        # Límite fijos = ingresos: disponible cero, no es error.
        ({"gastos_fijos": Decimal("3000000")}, Decimal("0")),
        # Límite gastado = saldo: el cupo queda justo en cero.
        ({"dia_actual": 30, "gastado_hasta_hoy": Decimal("3000000")}, Decimal("0")),
        # Un peso antes de ese borde: queda $1 para el último día.
        ({"dia_actual": 30, "gastado_hasta_hoy": Decimal("2999999")}, Decimal("1")),
        # Partición «todo en cero»: sin ingresos no hay cupo, pero no es error.
        ({"ingresos_mensuales": Decimal("0")}, Decimal("0")),
    ],
    ids=["mes-28", "mes-31", "dia-1", "fijos-igual-ingresos", "gastado-igual-saldo",
         "gastado-un-peso-menos", "ingresos-cero"],
)
def test_limites_validos(cambios, esperado):
    assert calcular_limite_diario(**{**BASE, **cambios}) == esperado


@pytest.mark.parametrize(
    ("cambios", "error"),
    [
        # dias_del_mes 27: último valor inválido por debajo.
        ({"dias_del_mes": 27}, ValueError),
        # dias_del_mes 32: primer valor inválido por encima.
        ({"dias_del_mes": 32}, ValueError),
        # dia_actual 0: el día anterior al primero.
        ({"dia_actual": 0}, ValueError),
        # Días como float: tipo inválido.
        ({"dias_del_mes": 30.0}, ValueError),
        # Meta un peso por encima de lo disponible.
        ({"gastos_fijos": Decimal("400000"), "meta_ahorro": Decimal("2600001")},
         MetaInalcanzableError),
        # Gastos fijos un peso por encima de los ingresos.
        ({"gastos_fijos": Decimal("3000001")}, GastosSuperanIngresosError),
        # Cada monto en -1, el primer valor negativo.
        ({"ingresos_mensuales": Decimal("-1")}, MontoInvalidoError),
        ({"gastos_fijos": Decimal("-1")}, MontoInvalidoError),
        ({"gastado_hasta_hoy": Decimal("-1")}, MontoInvalidoError),
        # Monto como texto: tipo inválido.
        ({"meta_ahorro": "300000"}, MontoInvalidoError),
    ],
    ids=["mes-27", "mes-32", "dia-0", "dias-float", "meta-mas-1", "fijos-mas-1",
         "ingresos-negativos", "fijos-negativos", "gastado-negativo", "meta-texto"],
)
def test_fuera_de_los_limites_lanza_el_error_exacto(cambios, error):
    with pytest.raises(error) as excinfo:
        calcular_limite_diario(**{**BASE, **cambios})

    # pytest.raises acepta subclases: esto exige el tipo exacto.
    assert excinfo.type is error
