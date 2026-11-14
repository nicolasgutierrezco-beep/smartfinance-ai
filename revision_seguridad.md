# Informe de revisión de código y seguridad

Proyecto: SmartFinance AI
Estudiante: Nicolás Andrés Gutiérrez Collazos
Fecha: 2026-11-14
Commit revisado: `6fe5142` (último commit de la semana 5, antes de las correcciones)

## 1. Herramientas y criterios

- **Linter:** ruff 0.16.9 con las reglas E, F, B, S y UP. Configuración en `pyproject.toml`.
  Se corre con `ruff check .` y queda en `All checks passed!`.
- **Auditoría de dependencias:** pip-audit — **pendiente de ejecutar en el equipo local**
  (ver sección 4). La revisión se hizo en un entorno sin acceso a internet, y pip-audit
  necesita consultar la base de vulnerabilidades en línea. Lo que sí se verificó: el
  proyecto tiene **una sola dependencia**, `pytest==9.1.1`, con versión fijada, y solo
  sirve para las pruebas. La función en sí usa únicamente la librería estándar de Python.
- **Lista de revisión:** la de la semana 6 (corrección y pruebas, diseño y legibilidad,
  seguridad), aplicada a `src/smartfinance/presupuesto.py` y `tests/test_presupuesto.py`.
  Además de leer, se **ejecutaron a mano casos límite con datos reales**; así salieron los
  dos hallazgos de más peso (H-02 y H-03).
- **Revisión con IA:** Claude, con el prompt que está en la sección 3.

### Puntos de seguridad revisados

| Punto | ¿Aplica? | Resultado |
|---|---|---|
| Inyección (consultas con parámetros) | **No, todavía.** La funcionalidad no tiene base de datos ni arma consultas: es una cuenta matemática que recibe números y devuelve un número. | Sin hallazgos. Cuando entre PostgreSQL (ADR-001) toda consulta irá con parámetros; queda anotado en pendientes. |
| Secretos (código, historial, .gitignore, .env.example) | **Sí.** | Sin hallazgos. Se buscó en **todo el historial de Git** (`git log --all -p`) con un patrón para claves, contraseñas y tokens: 0 coincidencias reales. `.env` y `firebase-credentials.json` están en `.gitignore`. Se creó `.env.example` (H-05). |
| Contraseñas (scrypt, bcrypt o argon2 con sal) | **No, todavía.** El código no guarda usuarios ni contraseñas. | El modelo de datos de la semana 4 define `password_hash`; cuando se implemente el registro de usuarios se usará bcrypt o argon2, nunca MD5 ni SHA-1. |
| Control de acceso (rol verificado y prueba de abuso) | **No, todavía.** No hay usuarios, roles ni operaciones restringidas: la función no sabe quién la llama. | La «prueba de abuso» que sí aplica a una función pura es la de **entrada hostil**: se agregaron 5 pruebas de error nuevas (float, bool, día inexistente, fijos mayores que ingresos, etc.). |
| Dependencias (existen, necesarias, versión fijada, pip-audit) | **Sí.** | `pytest==9.1.1` existe, es necesaria para las pruebas y está fijada. pip-audit pendiente (sección 4). |

## 2. Tabla de hallazgos

| Id | Archivo y línea | Problema | Categoría (OWASP o tipo) | Severidad | Corrección | Commit |
|---|---|---|---|---|---|---|
| H-01 | `presupuesto.py:48` en `6fe5142` (hoy línea 81) | `"{:,.0f}".format(monto)` en vez de f-string (UP032) | Estilo / legibilidad | Baja | f-string: `f"{monto:,.0f}"` | `051bdc7` |
| H-02 | `presupuesto.py:143-156` | Con gastos fijos mayores que los ingresos, el mensaje decía «La meta supera tu disponibilidad mensual (**$-200.000** COP máximo)». Un máximo negativo no significa nada para el usuario. | Error de lógica / validación de entrada | **Media** | Nueva excepción `GastosSuperanIngresosError` con las dos cifras y un mensaje claro. Prueba nueva: `test_gastos_fijos_mayores_que_los_ingresos_avisan_claro`. | `6789feb` |
| H-03 | `presupuesto.py:129-134` | Un `float` (`1500000.0`) reventaba con `TypeError: unsupported operand type(s) for -: 'float' and 'decimal.Decimal'`, un error interno de Python. Y `True` colaba como «día 1» porque en Python un bool es un int. | Validación de entrada / robustez (A03-adyacente: entrada no validada) | **Media** | `_como_monto` acepta Decimal o int y rechaza float y bool con `MontoInvalidoError`; `_como_dia` acepta solo enteros. 3 pruebas nuevas. | `8b659b8` |
| H-04 | `pyproject.toml` (no existía) | El proyecto no tenía linter configurado: ruff corría con reglas por defecto y nadie revisaba sus avisos. | Proceso / calidad | Baja | `pyproject.toml` con E, F, B, S, UP y la justificación de S101 escrita. | `8e77108` |
| H-05 | `.env.example` (no existía) | Faltaba la plantilla de variables de entorno que exige la lista de la semana. `firebase-credentials.json` no estaba en `.gitignore`. | A05 Configuración insegura / secretos | Baja | `.env.example` con las variables del ADR-001 y valores de ejemplo inservibles; Firebase en `.gitignore`. | `5007e34` |
| H-07 | `.gitignore:3` | La regla `.env.*` (de la semana 5) también bloqueaba `.env.example`, así que el commit `5007e34` que decía agregarlo **solo subió el `.gitignore`**. El archivo existía en mi carpeta pero no en el repositorio. Lo detectó la prueba final de clonar en una carpeta limpia. | A05 Configuración / proceso | Baja | Excepción `!.env.example` en `.gitignore` y commit del archivo. Lección: después de un `git add`, mirar `git show --stat` antes de dar algo por subido. | `ver abajo` |
| H-06 | `presupuesto.py:20` y `:92` | El docstring de `MontoInvalidoError` decía solo «monto en negativo», y desde H-03 también cubre float y bool. El de la función principal no decía qué recibe, qué devuelve ni qué errores lanza. | Mantenibilidad / documentación | Baja | Docstrings completos (Args, Returns, Raises, Ejemplo). El ejemplo se verifica con `python -m doctest`. | `11c8723` |

**Severidad:** alta (permite acceder o cambiar datos sin permiso, o expone secretos), media (error probable o riesgo con condiciones), baja (estilo o mantenibilidad).

Ningún hallazgo fue de severidad alta: la función no maneja datos de otros usuarios, no
guarda nada y no tiene secretos. Los dos de severidad media (H-02 y H-03) son errores que
un usuario real sí habría visto.

### Avisos del linter no corregidos

| Regla | Archivo y línea | Por qué se mantiene |
|---|---|---|
| S101 | `tests/test_presupuesto.py` (15 líneas, una por prueba) | `assert` es la forma normal de comprobar en pytest. El aviso existe porque Python elimina los `assert` al correr con `-O`, y eso sería grave en código de producción; en las pruebas no aplica. Silenciado **solo para la carpeta `tests/`** en `pyproject.toml`; en `src/` la regla sigue activa. |

## 3. Revisión con IA

**Prompt usado** (a Claude, sobre el código ya corregido en H-01 a H-05):

> Revisa `src/smartfinance/presupuesto.py` y `tests/test_presupuesto.py` con estos
> criterios: corrección frente al contrato del README, casos límite, seguridad (OWASP:
> inyección, secretos, validación de entrada), legibilidad (nombres, valores mágicos,
> funciones largas, duplicación) y mantenibilidad. Entrega una tabla con archivo y línea,
> problema, categoría y severidad (alta, media o baja). Separa los **problemas seguros**
> de las **sospechas** que habría que confirmar ejecutando el código. No propongas
> cambios a las pruebas.

Cada fila se verificó en el código antes de clasificarla. Los números de línea son los del
archivo final de esta rama, para que se puedan ubicar al abrirlo.

| Hallazgo de la IA | ¿Real o falso positivo? | Cómo lo verifiqué |
|---|---|---|
| **Seguro.** Línea 20: el docstring de `MontoInvalidoError` dice «monto en negativo», pero la clase también se lanza para float y bool. | **Real** (baja). Corregido en H-06. | Leí los dos sitios donde se lanza (líneas 42 y 63): uno es por tipo, otro por signo. El docstring solo mencionaba el segundo. |
| **Seguro.** Línea 92: la función principal tenía un docstring de una línea; no documentaba parámetros, retorno ni los cuatro errores. | **Real** (baja). Corregido en H-06. | Comparé el docstring con la firma y con los `raise` del cuerpo. Faltaban los cuatro. |
| **Seguro.** Líneas 41 y 52: la guarda `isinstance(valor, bool)` está repetida en `_como_monto` y `_como_dia`. | **Real, pero se mantiene.** | Son dos líneas, en dos funciones que aceptan tipos distintos y lanzan errores distintos. Extraer una tercera función solo para esa comparación agrega una capa más para leer sin quitar lógica repetida de verdad. |
| **Sospecha.** Línea 167: «posible división por cero si `dias_restantes` llega a 0». | **Falso positivo.** | `_exigir_que_el_dia_exista` (línea 75) garantiza `1 <= dia_actual <= dias_del_mes`, así que `dias_del_mes - dia_actual + 1` es como mínimo 1. El peor caso, último día del mes, está cubierto por `test_el_ultimo_dia_del_mes_concentra_todo_el_saldo` y da 1 día, no 0. |
| **Sospecha.** Línea 81: `_en_pesos` no maneja negativos; un `-1000` saldría como «-1.000» y rompería el formato. | **Falso positivo.** | Seguí el orden de las validaciones: todo monto que llega a `_en_pesos` ya pasó por `_exigir_que_no_sea_negativo` (líneas 136-139), y `disponible_del_mes` se comprueba `>= 0` en la línea 144 antes de formatearse en la 155. Hoy es imposible que reciba un negativo. |
| **Sospecha.** Líneas 84-91: seis parámetros son demasiados; propone agruparlos en una `dataclass`. | **Real, pero se pospone** (baja). Va en pendientes. | Son seis, dos con valor por defecto, y todas las llamadas usan nombres (`meta_ahorro=...`), así que se lee bien. Cuando exista la capa HTTP del ADR-001, un modelo de Pydantic hará ese papel de forma natural; crear una dataclass ahora sería duplicarlo después. |
| **Sospecha.** Línea 88: `dias_del_mes` debería calcularse con `calendar.monthrange` en vez de pedirlo. | **Falso positivo: es una decisión de diseño.** | La función no lee fechas ni el reloj **a propósito** (bitácora de la semana 5, entrada 6): así el mismo dato da siempre el mismo resultado y las pruebas son repetibles. Quien la llame decide de dónde saca los días. |
| **Sospecha.** Línea 64: el mensaje dice «monto numérico **positivo**», pero el cero se acepta (una meta de $0 es válida). | **Real, pero se mantiene** (baja). | Es cierto: estrictamente, cero no es positivo. Se mantiene porque es el texto literal del criterio de aceptación de HU-07 («El valor de la meta debe ser un monto numérico positivo»). El docstring ahora aclara que la meta «puede ser cero». |

**Lo que la IA no encontró:** el hallazgo **H-02**, el «máximo negativo». Ni el linter
(ruff con E, F, B, S) ni la revisión por lectura lo detectaron, porque el código era
sintácticamente perfecto y la lógica parecía correcta. Salió al **ejecutar a mano** la
función con un caso real: alguien que paga $1.000.000 de gastos fijos ganando $800.000.
La lección para el resto del proyecto: las herramientas revisan la forma del código; los
casos del negocio los tiene que probar, con números de verdad, quien entiende el negocio.

## 4. Pendientes

| Pendiente | Por qué no se corrigió todavía | Plan |
|---|---|---|
| Ejecutar `pip-audit` | La revisión se hizo en un entorno sin internet y pip-audit consulta una base de vulnerabilidades en línea. | Antes de entregar, en el equipo local y con el entorno activo: `pip install pip-audit` y luego `pip-audit -r requirements.txt`. Pegar el resultado en esta tabla. Riesgo bajo: la única dependencia es pytest, y solo para pruebas. |
| Agrupar los seis parámetros en un modelo | Es una mejora de diseño, no un error, y hacerla ahora se duplicaría después. | Cuando entre la capa HTTP con FastAPI (ADR-001), el modelo de Pydantic del `POST /api/v1/metas-ahorro` será ese agrupador, con la misma validación de tipos que hoy hacen `_como_monto` y `_como_dia`. |
| Prueba de abuso de control de acceso | No hay usuarios ni roles todavía. | En la semana en que se implemente autenticación: una prueba en la que el usuario A intenta leer o cambiar la meta de ahorro del usuario B y recibe 403. |
| Consultas con parámetros | No hay base de datos todavía. | Al conectar PostgreSQL, toda consulta va con parámetros (nunca concatenando texto) y se agrega una prueba de inyección con la frase `'; DROP TABLE transacciones;--` que ya está en la propuesta de la semana 2. |

**Claves expuestas:** Ninguna. Se revisó el historial completo de Git, en todas las ramas,
con `git log --all -p` filtrado por patrones de claves, contraseñas y tokens. Las únicas
coincidencias son los valores de ejemplo de `.env.example` (`pon_aqui_tu_clave_real`,
`cambia_esta_clave`), que no sirven para nada.
