"""Pruebas de HU-04: el límite de gasto diario.

Cada prueba lleva en el nombre lo que comprueba, para que al correr `pytest -v`
se pueda leer la lista como si fuera la especificación de la función.
"""

from decimal import Decimal

import pytest

from smartfinance.presupuesto import (
    GastosSuperanIngresosError,
    MetaInalcanzableError,
    MontoInvalidoError,
    calcular_limite_diario,
)

# ---------------------------------------------------------------------------
# Casos normales
# ---------------------------------------------------------------------------


def test_escenario_de_la_historia_da_cuarenta_mil_diarios():
    """HU-04, escenario 1: $1.500.000 de ingreso y meta de $300.000 en 30 días."""
    limite = calcular_limite_diario(
        ingresos_mensuales=Decimal("1500000"),
        gastos_fijos=Decimal("0"),
        meta_ahorro=Decimal("300000"),
        dias_del_mes=30,
    )

    assert limite == Decimal("40000")


def test_los_gastos_fijos_se_restan_antes_de_repartir():
    """Arriendo y servicios no son plata disponible, así que salen de la cuenta."""
    limite = calcular_limite_diario(
        ingresos_mensuales=Decimal("2000000"),
        gastos_fijos=Decimal("800000"),
        meta_ahorro=Decimal("200000"),
        dias_del_mes=31,
    )

    # Quedan $1.000.000 libres repartidos en 31 días.
    assert limite == Decimal("32258")


def test_a_mitad_de_mes_reparte_solo_el_saldo_entre_los_dias_que_faltan():
    """El caso de la propuesta: va en el día 19 y ya gastó $390.000 de $500.000."""
    limite = calcular_limite_diario(
        ingresos_mensuales=Decimal("2500000"),
        gastos_fijos=Decimal("1600000"),
        meta_ahorro=Decimal("400000"),
        dias_del_mes=30,
        dia_actual=19,
        gastado_hasta_hoy=Decimal("390000"),
    )

    # Quedan $110.000 para 12 días (del 19 al 30, contando hoy).
    assert limite == Decimal("9166")


# ---------------------------------------------------------------------------
# Casos límite
# ---------------------------------------------------------------------------


def test_meta_igual_a_la_disponibilidad_deja_el_cupo_en_cero():
    """Guardar todo lo que sobra es válido: el cupo queda en cero, no falla."""
    limite = calcular_limite_diario(
        ingresos_mensuales=Decimal("1000000"),
        gastos_fijos=Decimal("400000"),
        meta_ahorro=Decimal("600000"),
        dias_del_mes=30,
    )

    assert limite == Decimal("0")


def test_el_ultimo_dia_del_mes_concentra_todo_el_saldo():
    """Si hoy es el día 30 de un mes de 30, solo queda ese día para gastar."""
    limite = calcular_limite_diario(
        ingresos_mensuales=Decimal("1000000"),
        gastos_fijos=Decimal("0"),
        meta_ahorro=Decimal("400000"),
        dias_del_mes=30,
        dia_actual=30,
        gastado_hasta_hoy=Decimal("500000"),
    )

    assert limite == Decimal("100000")


def test_si_ya_se_paso_del_presupuesto_devuelve_cero_y_no_un_negativo():
    """Mostrar «puedes gastar -$4.166» no le sirve a nadie."""
    limite = calcular_limite_diario(
        ingresos_mensuales=Decimal("1000000"),
        gastos_fijos=Decimal("0"),
        meta_ahorro=Decimal("900000"),
        dias_del_mes=30,
        dia_actual=10,
        gastado_hasta_hoy=Decimal("150000"),
    )

    assert limite == Decimal("0")


def test_redondea_hacia_abajo_para_no_romper_la_meta():
    """$100 entre 3 días da $33,33: se devuelve $33, nunca $34."""
    limite = calcular_limite_diario(
        ingresos_mensuales=Decimal("1000000"),
        gastos_fijos=Decimal("0"),
        meta_ahorro=Decimal("999900"),
        dias_del_mes=30,
        dia_actual=28,
    )

    assert limite == Decimal("33")


def test_funciona_igual_en_un_mes_de_veintiocho_dias():
    """Febrero existe y el mes más corto no puede romper la cuenta."""
    limite = calcular_limite_diario(
        ingresos_mensuales=Decimal("1400000"),
        gastos_fijos=Decimal("0"),
        meta_ahorro=Decimal("0"),
        dias_del_mes=28,
    )

    assert limite == Decimal("50000")


# ---------------------------------------------------------------------------
# Casos de error
# ---------------------------------------------------------------------------


def test_meta_mayor_a_la_disponibilidad_avisa_con_el_maximo_posible():
    """HU-04, escenario 2: el mensaje tiene que decir hasta cuánto sí se puede."""
    with pytest.raises(MetaInalcanzableError) as error:
        calcular_limite_diario(
            ingresos_mensuales=Decimal("800000"),
            gastos_fijos=Decimal("700000"),
            meta_ahorro=Decimal("250000"),
            dias_del_mes=30,
        )

    assert str(error.value) == (
        "La meta supera tu disponibilidad mensual ($100.000 COP máximo)"
    )


def test_un_monto_en_negativo_se_rechaza():
    """HU-07, escenario 2: una meta de -$50.000 no tiene sentido."""
    with pytest.raises(MontoInvalidoError):
        calcular_limite_diario(
            ingresos_mensuales=Decimal("1500000"),
            gastos_fijos=Decimal("0"),
            meta_ahorro=Decimal("-50000"),
            dias_del_mes=30,
        )


def test_gastos_fijos_mayores_que_los_ingresos_avisan_claro():
    """Revisión S6, H-02: antes decía «$-200.000 COP máximo», que no significa nada."""
    with pytest.raises(GastosSuperanIngresosError) as error:
        calcular_limite_diario(
            ingresos_mensuales=Decimal("800000"),
            gastos_fijos=Decimal("1000000"),
            meta_ahorro=Decimal("0"),
            dias_del_mes=30,
        )

    mensaje = str(error.value)
    assert "$1.000.000" in mensaje and "$800.000" in mensaje
    assert "-$" not in mensaje and "$-" not in mensaje


def test_un_float_se_rechaza_con_un_mensaje_claro_y_no_con_un_typeerror():
    """Revisión S6, H-03: antes un float reventaba con «unsupported operand type»."""
    with pytest.raises(MontoInvalidoError) as error:
        calcular_limite_diario(
            ingresos_mensuales=1500000.0,  # float a propósito
            gastos_fijos=Decimal("0"),
            meta_ahorro=Decimal("300000"),
            dias_del_mes=30,
        )

    assert "float" in str(error.value)
    assert "Decimal" in str(error.value)


def test_un_booleano_no_cuela_como_dia_del_mes():
    """Revisión S6, H-03: True vale 1 en Python y antes pasaba como «día 1»."""
    with pytest.raises(ValueError):
        calcular_limite_diario(
            ingresos_mensuales=Decimal("1500000"),
            gastos_fijos=Decimal("0"),
            meta_ahorro=Decimal("300000"),
            dias_del_mes=30,
            dia_actual=True,
        )


def test_un_entero_normal_sigue_funcionando_como_monto():
    """Un int es exacto, así que se acepta igual que un Decimal."""
    limite = calcular_limite_diario(
        ingresos_mensuales=1500000,
        gastos_fijos=0,
        meta_ahorro=300000,
        dias_del_mes=30,
    )

    assert limite == Decimal("40000")


def test_un_dia_que_no_existe_en_ese_mes_se_rechaza():
    """No hay 31 de noviembre, así que pedir el cupo de ese día es un error."""
    with pytest.raises(ValueError):
        calcular_limite_diario(
            ingresos_mensuales=Decimal("1500000"),
            gastos_fijos=Decimal("0"),
            meta_ahorro=Decimal("300000"),
            dias_del_mes=30,
            dia_actual=31,
        )
