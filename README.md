# SmartFinance AI

Finanzas personales que aconsejan, no solo registran.

- **Estudiante:** Nicolás Andrés Gutiérrez Collazos
- **Seminario:** Inteligencia Artificial Aplicada al Ciclo de Vida del Software
- **Estado:** límite diario (HU-04), alertas y pagos de deudas (HU-03, HU-06) y recomendación
  por gasto en ocio (HU-02), con 76 pruebas (semana 7)

---

## 1. Qué es

SmartFinance AI es una aplicación de finanzas personales. La idea es que el usuario
escriba frases normales como «Pagué $15.000 en el súper», y la app clasifique el gasto
sola, le avise cuando se acerque el vencimiento de una tarjeta y le diga **cuánto puede
gastar hoy** sin romper la meta de ahorro que se puso para el mes.

Este repositorio tiene el primer pedazo que funciona de verdad: el cálculo del límite de
gasto diario (historia de usuario **HU-04**). Es una función de Python, con sus pruebas,
que recibe los números del mes y devuelve cuánto se puede gastar cada día que falta.

**Lo que hace hoy**

- Resta los gastos fijos de los ingresos para saber lo que de verdad hay disponible.
- Aparta la meta de ahorro y descuenta lo ya gastado.
- Reparte el saldo entre los días que faltan, contando el de hoy.
- Redondea **hacia abajo** y **nunca devuelve negativos**.
- Rechaza con un mensaje claro los datos que no tienen sentido: montos negativos,
  números con decimales flotantes, días que no existen, gastos fijos mayores que los
  ingresos, y metas imposibles.

**Desde la semana 7 también**

- Valida que una deuda nueva venza después de hoy y genera el recordatorio cuando faltan
  2 días, 1 día o vence hoy (HU-03), en `deudas.py`.
- Marca una deuda como pagada, impide pagarla dos veces y suma lo que falta por pagar (HU-06).
- Avisa cuando el gasto en ocio pasó el tope y dice cuánto recortar, siempre que haya al
  menos 5 transacciones (HU-02), en `recomendaciones.py`.

**Lo que todavía no hace** (viene en las siguientes semanas, según el diseño del ADR-001):
registrar gastos en lenguaje natural con la API del LLM, guardar en PostgreSQL, enviar
alertas con Firebase.

## 2. Requisitos

- **Python 3.11 o superior.** Se probó con 3.11 y 3.13.
- **pip**, que viene con Python.
- Nada más. La función usa solo la librería estándar de Python. La única dependencia
  externa es `pytest`, y solo sirve para correr las pruebas.

No necesita base de datos, ni conexión a internet, ni ninguna clave de API.

## 3. Instalación

Clona el repositorio y entra a la carpeta:

```bash
git clone <url-del-repositorio>
cd smartfinance-ai
```

Crea un entorno virtual y actívalo. En Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\activate
```

En Mac o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Si Windows te muestra un error de permisos al activar, ejecuta antes
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` en esa misma terminal.

Instala la dependencia de pruebas:

```bash
pip install -r requirements.txt
```

**Variables de entorno.** Hoy no hace falta ninguna. El archivo `.env.example` deja
declaradas las que va a necesitar la arquitectura completa (base de datos, Redis, API del
LLM, Firebase). Cuando llegue el momento, cópialo como `.env` y pon ahí los valores
reales; el `.env` nunca se sube al repositorio.

## 4. Ejecución

Todavía no hay interfaz ni servidor: la función se usa desde Python. Con el entorno
activo, desde la raíz del proyecto:

```bash
python -c "import sys; sys.path.insert(0, 'src'); from decimal import Decimal; from smartfinance.presupuesto import calcular_limite_diario as f; print(f(Decimal('1500000'), Decimal('0'), Decimal('300000'), 30))"
```

Debe imprimir `40000`: el escenario de la historia de usuario.

Para jugar con otros números es más cómodo abrir Python y escribir paso a paso:

```python
import sys; sys.path.insert(0, "src")
from decimal import Decimal
from smartfinance.presupuesto import calcular_limite_diario

# Camila: gana $2.500.000, paga $1.600.000 de fijos, quiere ahorrar $400.000.
# Va en el día 19 y ya gastó $390.000 de su presupuesto libre.
calcular_limite_diario(
    ingresos_mensuales=Decimal("2500000"),
    gastos_fijos=Decimal("1600000"),
    meta_ahorro=Decimal("400000"),
    dias_del_mes=30,
    dia_actual=19,
    gastado_hasta_hoy=Decimal("390000"),
)
# Decimal('9166')  ->  le quedan $110.000 para 12 días
```

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

| Parámetro | Tipo | Qué significa |
| --- | --- | --- |
| `ingresos_mensuales` | `Decimal` o `int` | Lo que entra en el mes, en pesos. No negativo. |
| `gastos_fijos` | `Decimal` o `int` | Lo ya comprometido: arriendo, servicios, cuotas. No negativo. |
| `meta_ahorro` | `Decimal` o `int` | Lo que se quiere guardar este mes. Puede ser cero. |
| `dias_del_mes` | `int` | Entre 28 y 31. |
| `dia_actual` | `int` | De 1 a `dias_del_mes`. Por defecto 1. Hoy todavía cuenta. |
| `gastado_hasta_hoy` | `Decimal` o `int` | Lo ya gastado del presupuesto libre. Por defecto 0. |

**Devuelve** un `Decimal` en pesos enteros, redondeado hacia abajo, nunca negativo.

**Errores que lanza**

| Situación | Error | Mensaje |
| --- | --- | --- |
| Un monto en negativo | `MontoInvalidoError` | «El valor de la meta debe ser un monto numérico positivo» |
| Un `float` o un `bool` como monto | `MontoInvalidoError` | «… llegó como float; debe ser Decimal (o un entero)…» |
| Días fuera de 28..31, o día fuera del mes, o no entero | `ValueError` | «El día actual debe estar dentro del mes» |
| Gastos fijos mayores que los ingresos | `GastosSuperanIngresosError` | «Tus gastos fijos ($1.000.000 COP) superan tus ingresos ($800.000 COP)…» |
| Meta mayor que lo disponible | `MetaInalcanzableError` | «La meta supera tu disponibilidad mensual ($100.000 COP máximo)» |

**Casos límite que la función maneja a propósito**

| Situación | Qué hace |
| --- | --- |
| Meta igual a la disponibilidad | Devuelve `0`. Todo el sobrante va al ahorro; no es error. |
| Hoy es el último día del mes | Todo el saldo se concentra en ese día. |
| Ya se gastó más del presupuesto libre | Devuelve `0`, nunca un número en rojo. |
| La división no da exacta | Redondea hacia abajo: $9.166,67 → $9.166. |

Los supuestos están explicados en el docstring de la función
(`src/smartfinance/presupuesto.py`), que además trae un ejemplo que `doctest` ejecuta.

## 5. Pruebas

Con el entorno activo, un solo comando corre las 76 pruebas:

```bash
pytest
```

Para verlas con su nombre, una por una:

```bash
pytest -v
```

Los nombres se leen como frases y funcionan como la especificación de la función:
`test_redondea_hacia_abajo_para_no_romper_la_meta`,
`test_si_ya_se_paso_del_presupuesto_devuelve_cero_y_no_un_negativo`, etcétera.

Están repartidas así:

| Archivo | Cuántas | Qué prueba |
| --- | --- | --- |
| `test_presupuesto.py` | 15 | HU-04: casos normales, límite y de error (semanas 5 y 6, sin cambios) |
| `test_presupuesto_tabla.py` | 17 | HU-04: particiones y valores límite que faltaban (semana 7) |
| `test_deudas.py` | 26 | HU-03 y HU-06, con tabla de decisión para la alerta |
| `test_recomendaciones.py` | 18 | HU-02, con tabla de decisión |

`tests/conftest.py` tiene los datos sintéticos (fixtures) que usan las pruebas. El diseño
de cada caso, de dónde sale su esperado y la revisión de las pruebas generadas con IA
están en `registro_pruebas.md`.

**Linter.** El proyecto tiene `ruff` configurado en `pyproject.toml` con reglas de
estilo, errores, errores probables y seguridad (E, F, B, S, UP). Para correrlo:

```bash
pip install ruff
ruff check .
```

Debe decir `All checks passed!`. El único aviso silenciado es `S101` dentro de `tests/`,
porque ahí el `assert` es la forma normal de comprobar con pytest; la razón está escrita
en el mismo `pyproject.toml`.

## 6. Estructura del repositorio

```
smartfinance-ai/
├── README.md                      Este archivo
├── bitacora_ia.md                 Qué propuso la IA, qué se aceptó y qué se rechazó
├── revision_seguridad.md          Informe de revisión de código y seguridad (semana 6)
├── registro_pruebas.md            Reglas, tablas de casos y revisión de pruebas (semana 7)
├── pyproject.toml                 Datos del proyecto y configuración del linter
├── pytest.ini                     Dónde buscar el código y las pruebas
├── requirements.txt               Dependencias (solo pytest)
├── .env.example                   Plantilla de variables de entorno; el .env real no se sube
├── .gitignore                     Lo que nunca va al repositorio: .env, claves, cachés
├── src/
│   └── smartfinance/
│       ├── __init__.py
│       ├── presupuesto.py         calcular_limite_diario y sus errores (HU-04)
│       ├── deudas.py              Vencimientos, alertas y pagos de deudas (HU-03, HU-06)
│       └── recomendaciones.py     Recomendación por gasto en ocio (HU-02)
└── tests/
    ├── conftest.py                Datos sintéticos de prueba (fixtures)
    ├── test_presupuesto.py        Las 15 pruebas de las semanas 5 y 6
    ├── test_presupuesto_tabla.py  Límites y particiones de HU-04
    ├── test_deudas.py             Pruebas de HU-03 y HU-06
    └── test_recomendaciones.py    Pruebas de HU-02
```

## 7. Uso de IA

Este proyecto se construyó con un asistente de IA (Claude) como herramienta, y las
decisiones quedaron registradas. Tres archivos cuentan la historia completa:

- **`bitacora_ia.md`**: cada sugerencia importante del asistente, con la decisión que se
  tomó (aceptada, aceptada con cambios o rechazada), la razón y cómo se verificó. Incluye
  las entradas de la semana 5 (construcción), la semana 6 (revisión) y la semana 7
  (pruebas).
- **`registro_pruebas.md`**: las reglas de cada función, sus tablas de casos, qué pruebas
  de la IA se corrigieron o descartaron y por qué, y los errores introducidos a propósito.
- **`revision_seguridad.md`**: la revisión de código y seguridad de la semana 6, con los
  hallazgos del linter, de la lista de revisión y de una segunda revisión hecha con IA,
  cada uno clasificado como real o falso positivo después de verificarlo en el código.

La regla que se siguió: **la IA propone, el código se verifica**. Ninguna prueba se
modificó para que el código pasara; cuando una corrección cambió el comportamiento, se
agregó una prueba nueva para ese caso.

## 8. Autor y licencia

**Autor:** Nicolás Andrés Gutiérrez Collazos. Proyecto final del Seminario en Inteligencia
Artificial Aplicada al Ciclo de Vida del Software, Fundación Escuela Tecnológica de Neiva
Jesús Oviedo Pérez, 2026.

**Licencia:** MIT. Se puede usar, copiar y modificar citando al autor.
