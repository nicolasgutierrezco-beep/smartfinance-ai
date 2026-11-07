# SmartFinance AI

Aplicación de finanzas personales que entiende frases cotidianas, avisa de las facturas
por vencer y calcula cuánto se puede gastar al día sin romper la meta de ahorro del mes.

Este repositorio corresponde al proyecto final del Seminario en Inteligencia Artificial
Aplicada al Ciclo de Vida del Software.

- **Estudiante:** Nicolás Andrés Gutiérrez Collazos
- **Lenguaje:** Python 3.11
- **Pruebas:** pytest

---

## Funcionalidad de la semana 5

### La historia de usuario

**HU-04 · Calcular el límite de gasto diario según la meta de ahorro.** Prioridad: *Must*.

> **Como** usuario personal, **quiero** fijar una meta de ahorro mensual, **para que** el
> sistema me diga exactamente cuánto puedo gastar al día sin comprometerla.

**Escenario 1 — Cálculo del presupuesto diario (éxito)**

- **Dado que** el usuario fija una meta de ahorro de $300.000 COP para un mes de 30 días,
  con ingresos de $1.500.000 COP,
- **cuando** el sistema calcula el presupuesto,
- **entonces** asigna un margen máximo de gasto de $40.000 COP diarios.

**Escenario 2 — Meta superior a la capacidad financiera (error)**

- **Dado que** los ingresos netos son $800.000 COP y los gastos fijos $700.000 COP,
- **cuando** el usuario fija una meta de ahorro de $250.000 COP,
- **entonces** el sistema muestra «La meta supera tu disponibilidad mensual
  ($100.000 COP máximo)».

### El contrato de la función

```python
def calcular_limite_diario(
    ingresos_mensuales: Decimal,
    gastos_fijos: Decimal,
    meta_ahorro: Decimal,
    dias_del_mes: int,
    dia_actual: int = 1,
    gastado_hasta_hoy: Decimal = Decimal("0"),
) -> Decimal:
```

**Qué recibe**

| Parámetro | Tipo | Qué significa |
| --- | --- | --- |
| `ingresos_mensuales` | `Decimal` | Lo que entra en el mes, en pesos. No puede ser negativo. |
| `gastos_fijos` | `Decimal` | Lo que ya está comprometido: arriendo, servicios, cuotas. No puede ser negativo. |
| `meta_ahorro` | `Decimal` | Lo que la persona quiere guardar este mes. No puede ser negativa. |
| `dias_del_mes` | `int` | Cuántos días tiene el mes. Entre 28 y 31. |
| `dia_actual` | `int` | En qué día va el mes. Por defecto 1. El día de hoy todavía cuenta. |
| `gastado_hasta_hoy` | `Decimal` | Lo que ya se gastó del presupuesto libre. Por defecto 0. |

**Qué devuelve**

Un `Decimal` con el máximo que se puede gastar hoy y cada uno de los días que quedan,
en pesos enteros. Nunca devuelve centavos y nunca devuelve un número negativo.

**Cómo hace la cuenta**

En palabras simples, la plata se reparte en tres montones y solo el tercero se puede gastar:

1. De los ingresos se restan los gastos fijos. Lo que queda es la **disponibilidad del mes**.
2. De esa disponibilidad se aparta la meta de ahorro. Lo que sobra es el **presupuesto libre**.
3. A ese presupuesto libre se le descuenta lo que ya se gastó, y el saldo se divide entre
   los días que faltan, incluido hoy.

**Supuestos**

- Todos los montos están en pesos colombianos y la función no maneja centavos, porque en
  Colombia no circulan.
- El resultado se redondea **hacia abajo**. Si la cuenta da $9.166,67 la función devuelve
  $9.166. Redondear hacia arriba sería darle permiso a la persona de pasarse de la meta.
- Los días que faltan incluyen el día de hoy. Si hoy es 1 de un mes de 30 días, quedan 30
  días, no 29.
- La función solo calcula. No guarda nada en la base de datos ni llama a ninguna IA.

**Casos límite**

| Situación | Qué hace la función |
| --- | --- |
| La meta es exactamente igual a la disponibilidad | Devuelve `0`. No es un error: significa que todo el sobrante va al ahorro. |
| Hoy es el último día del mes | Reparte todo el saldo en ese único día. |
| Ya se gastó más del presupuesto libre | Devuelve `0`, nunca un número negativo. |
| La meta supera la disponibilidad | Lanza `MetaInalcanzableError` con el máximo posible en el mensaje. |
| Un monto viene en negativo | Lanza `MontoInvalidoError`. |
| El día actual no existe en ese mes | Lanza `ValueError`. |

**Ejemplos**

```python
from decimal import Decimal
from smartfinance.presupuesto import calcular_limite_diario

# 1. El escenario de la historia de usuario: inicio de mes, sin gastos fijos.
calcular_limite_diario(
    ingresos_mensuales=Decimal("1500000"),
    gastos_fijos=Decimal("0"),
    meta_ahorro=Decimal("300000"),
    dias_del_mes=30,
)
# Decimal('40000')

# 2. A mitad de mes, con gastos fijos y plata ya gastada.
calcular_limite_diario(
    ingresos_mensuales=Decimal("2500000"),
    gastos_fijos=Decimal("1600000"),
    meta_ahorro=Decimal("400000"),
    dias_del_mes=30,
    dia_actual=19,
    gastado_hasta_hoy=Decimal("390000"),
)
# Decimal('9166')   -> quedan $110.000 para 12 días

# 3. Alguien que ya se pasó: el cupo es cero, no un número en rojo.
calcular_limite_diario(
    ingresos_mensuales=Decimal("1000000"),
    gastos_fijos=Decimal("0"),
    meta_ahorro=Decimal("900000"),
    dias_del_mes=30,
    dia_actual=10,
    gastado_hasta_hoy=Decimal("150000"),
)
# Decimal('0')

# 4. La meta no cabe: la función avisa en lugar de devolver un número imposible.
calcular_limite_diario(
    ingresos_mensuales=Decimal("800000"),
    gastos_fijos=Decimal("700000"),
    meta_ahorro=Decimal("250000"),
    dias_del_mes=30,
)
# MetaInalcanzableError: La meta supera tu disponibilidad mensual ($100.000 COP máximo)
```

### Cómo ejecutar las pruebas

```bash
pip install -r requirements.txt
pytest
```

Un solo comando corre las 11 pruebas. Para verlas una por una con su nombre:

```bash
pytest -v
```

---

## Estructura del repositorio

```
smartfinance-ai/
├── README.md                          Este archivo
├── bitacora_ia.md                     Registro de cómo se usó la IA
├── requirements.txt                   Dependencias
├── src/
│   └── smartfinance/
│       └── presupuesto.py             La funcionalidad de la semana 5
└── tests/
    └── test_presupuesto.py            Las pruebas
```
