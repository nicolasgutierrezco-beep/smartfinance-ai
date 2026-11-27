# Registro de pruebas: tabla de casos y pruebas de la IA

Proyecto: SmartFinance AI
Estudiante: Nicolás Andrés Gutiérrez Collazos
Fecha: 2026-11-22

En esta versión simplifiqué el código para que fuera fácil de explicar. Probé tres
funciones con reglas de negocio: calcular_limite_diario (HU-04),
validar_fecha_vencimiento (HU-03) y evaluar_gasto_ocio (HU-02). La última combina
varias condiciones, por eso tiene tabla de decisión. En total son 35 pruebas y todas
pasan con pytest -v. Las 15 pruebas de tests/test_presupuesto.py son de las semanas 5
y 6 y no las cambié.

## 1. Tabla de casos

### Regla 1: calcular_limite_diario (HU-04)

Regla: el límite diario es (ingresos - gastos fijos - meta de ahorro - lo gastado) dividido
entre los días que faltan del mes contando hoy. Se redondea hacia abajo al peso y nunca
es negativo. El mes tiene entre 28 y 31 días. Si la meta es mayor que lo disponible, o
los gastos fijos son mayores que los ingresos, se avisa con un error. En la historia, con
ingresos de $1.500.000, meta de $300.000 y un mes de 30 días, el límite es $40.000.

| Técnica | Partición o límite | Entrada | Esperado | Prueba que lo cubre |
|---|---|---|---|---|
| Partición válida | Caso de la historia | 1.500.000, meta 300.000, 30 días | 40.000 | test_escenario_de_la_historia_da_cuarenta_mil_diarios |
| Límite | Mes de 27 días | 27 días | ValueError | test_meses_invalidos_dan_error[27] |
| Límite | Mes de 28 días | 3.000.000 en 28 días | 107.142 | test_meses_validos[28-esperado0] |
| Límite | Mes de 31 días | 3.000.000 en 31 días | 96.774 | test_meses_validos[31-esperado1] |
| Límite | Mes de 32 días | 32 días | ValueError | test_meses_invalidos_dan_error[32] |
| Límite | Meta igual a lo disponible | Meta igual a lo que queda | 0 | test_meta_igual_a_la_disponibilidad_deja_el_cupo_en_cero |
| Límite | Meta un peso por encima | 3.000.000 de ingresos, meta 3.000.001 | MetaInalcanzableError | test_meta_un_peso_mayor_que_lo_disponible |
| Límite | Gastos fijos un peso por encima | 3.000.000 de ingresos, fijos 3.000.001 | GastosSuperanIngresosError | test_gastos_fijos_un_peso_mayores_que_los_ingresos |
| Partición inválida | Monto negativo | Un monto en negativo | MontoInvalidoError | test_un_monto_en_negativo_se_rechaza |
| Partición inválida | Día que no existe | Día 31 en un mes de 30 | ValueError | test_un_dia_que_no_existe_en_ese_mes_se_rechaza |

Los esperados de 28 y 31 días los calculé a mano: 3.000.000 / 28 = 107.142,8 y
3.000.000 / 31 = 96.774,1, redondeados hacia abajo.

### Regla 2: validar_fecha_vencimiento (HU-03)

Regla: según el escenario 2 de HU-03, la fecha de vencimiento de una deuda nueva debe ser
posterior a la fecha actual. Si no, se muestra "La fecha de vencimiento debe ser posterior
a la fecha actual". En las pruebas, hoy es el 13 de noviembre de 2026.

| Técnica | Partición o límite | Entrada | Esperado | Prueba que lo cubre |
|---|---|---|---|---|
| Partición inválida | Fecha pasada | 10/10/2026 | ValueError | test_fecha_de_hoy_o_anterior_da_error[fecha0] |
| Límite | Ayer | 12/11/2026 | ValueError | test_fecha_de_hoy_o_anterior_da_error[fecha1] |
| Límite | Hoy (A-01) | 13/11/2026 | ValueError | test_fecha_de_hoy_o_anterior_da_error[fecha2] |
| Límite | Mañana | 14/11/2026 | Se acepta | test_fecha_futura_se_acepta[fecha0] |
| Partición válida | Fecha lejana | 31/01/2027 | Se acepta | test_fecha_futura_se_acepta[fecha1] |

### Regla 3: evaluar_gasto_ocio (HU-02)

Regla: según el escenario 2 de HU-02, si hay menos de 5 transacciones se responde "Se
requieren al menos 5 transacciones registradas para generar sugerencias personalizadas".
Según el escenario 1, si el gasto en ocio supera el tope, se recomienda recortar. La
función suma solo los gastos de la categoría Ocio y devuelve cuánto se pasó del tope, o 0
si no se pasó. En las pruebas el tope es $100.000.

Tabla de decisión:

| Regla | ¿Hay 5 o más transacciones? | ¿El ocio supera el tope? | Resultado |
|---|---|---|---|
| R1 | No | No importa | ValueError |
| R2 | Sí | No | 0 |
| R3 | Sí | Sí | Lo que se pasó del tope |

Son dos condiciones, que darían 4 combinaciones, pero quedan 3 porque si no hay 5
transacciones no importa cuánto se gastó en ocio: siempre es error.

| Técnica | Partición o límite | Entrada | Esperado | Prueba que lo cubre |
|---|---|---|---|---|
| Partición inválida (R1) | Lista vacía | 0 transacciones | ValueError | test_lista_vacia_da_error |
| Partición inválida (R1) | Escenario 2 de la historia | 2 transacciones | ValueError | test_pocas_transacciones_da_error[2] |
| Límite (R1) | Último valor sin historial | 4 transacciones | ValueError | test_pocas_transacciones_da_error[4] |
| Límite (R2) | Un peso por debajo del tope | Ocio 99.999 | 0 | test_tabla_de_decision[99999-0] |
| Límite (R2) | Igual al tope (A-05) | Ocio 100.000 | 0 | test_tabla_de_decision[100000-0] |
| Límite (R3) | Un peso por encima | Ocio 100.001 | 1 | test_tabla_de_decision[100001-1] |
| Partición válida (R3) | Escenario 1 de la historia (A-04) | Ocio 120.000 | 20.000 | test_tabla_de_decision[120000-20000] |
| Partición válida (R3) | Con centavos | Ocio 100.000,50 | 0,50 (con pytest.approx) | test_tabla_de_decision[100000.5-0.5] |
| Partición válida (R3) | Datos sintéticos del mes | 9 gastos, ocio 121.900 | 21.900 | test_con_los_gastos_del_mes |

### Dudas en las reglas

Las numero como en la versión anterior del registro. Las demás eran de funciones que quité
al simplificar el código.

- A-01: la historia dice que la fecha debe ser posterior a hoy, pero no aclara si el mismo
  día cuenta. Lo dejé como inválido, porque "posterior" significa después. Toca
  confirmarlo con el profesor.
- A-04: el escenario 1 de HU-02 dice que se recomienda reducir $30.000, pero el gasto es
  $120.000 y el tope $100.000, así que la diferencia es $20.000. No encontré de dónde sale
  $30.000. Dejé que la función devuelva la diferencia, $20.000, y queda pendiente
  confirmarlo con el profesor.
- A-05: no está claro si gastar exactamente el tope es "superarlo". Lo dejé como que no,
  porque superar es pasarse. 

## 2. Pruebas de la IA descartadas o corregidas

Las pruebas pasaron por dos momentos.

Primera versión. Le pedí a la IA un borrador de pruebas con pytest a partir de las reglas
y las tablas, usando parametrize, pytest.raises con el tipo de error y esperados fijos.
Entregó 25 pruebas y 3 fallaron. Antes de tocar las pruebas que fallaron se revisó la
regla, y en las tres el error estaba en la prueba, no en el código. La IA también propuso
la revisión del resto del borrador con las tres preguntas (¿el esperado sale de la regla?,
¿fallaría si rompo el código?, ¿cubre algo que otra no cubre?) y yo acepté sus cambios.

Segunda versión. La primera versión terminó con 76 pruebas y mucho código difícil de
explicar. Decidí simplificarla y quedarme solo con lo que pide la tarea: tres funciones
con reglas, una con tabla de decisión. Quité las pruebas de funciones que ya no existen
y las de tipos inválidos. Quedaron 35 pruebas (20 nuevas y las 15 de las semanas 5 y 6).

| Prueba generada | Decisión | Por qué | En su lugar |
|---|---|---|---|
| test_fecha_hoy_es_valida: esperaba que una deuda que vence hoy se aceptara | Corregida | Falló, y al revisar la regla vi que dice "posterior a la fecha actual", así que hoy no vale (A-01) | test_fecha_de_hoy_o_anterior_da_error[fecha2] |
| test_escenario_gherkin_recomienda_reducir: esperaba $30.000 | Corregida | Falló. Copiaba el número de la historia, pero $120.000 - $100.000 da $20.000 (A-04) | test_tabla_de_decision[120000-20000] |
| test_deuda_con_monto_cero_lanza_error | Descartada | Falló. Usaba la regla de "monto positivo" de HU-07, que es para la meta de ahorro y no para deudas. Era una regla inventada | Nada, la clase Deuda ya no existe |
| test_historial_insuficiente con pytest.raises(ValueError) sin mensaje | Corregida | Pasaba con cualquier ValueError, aunque fuera otro error | test_pocas_transacciones_da_error, que revisa también el mensaje de la regla |
| test_sin_recomendacion_si_no_supera con 50.000 y 80.000 | Descartadas | Redundantes: están en la misma partición que 99.999, que además es el límite | test_tabla_de_decision[99999-0] |
| test_con_datos_sinteticos: solo revisaba que hubiera alguna respuesta | Corregida | Era débil: pasaba con cualquier resultado | test_con_los_gastos_del_mes, con el esperado fijo 21.900 calculado a mano |
| test_total_pendiente: calculaba el esperado con la misma suma que el código | Descartada | El esperado salía del código y no de la regla. Además, la función se quitó al simplificar | Nada |
| Pruebas de alertas, pagos de deudas y tipos inválidos (versión de 76 pruebas) | Descartadas al simplificar | Probaban funciones que quité porque no las pide la rúbrica y eran difíciles de explicar | Nada |

Las 20 pruebas nuevas las revisé con las mismas tres preguntas. Todos los esperados salen
de las reglas de la sección 1 o de cuentas hechas a mano. Las pruebas sí fallan cuando
se rompe el código, como se ve en la sección 3. Y cada prueba cubre una partición o un
límite distinto; por ejemplo, la de 2 transacciones es el escenario de la historia y la
de 4 es el último valor antes del mínimo.

Un detalle: en la primera versión se cambió pytest.approx por igualdad exacta porque los
montos eran Decimal. En la versión simple los montos son números normales, así que usé
pytest.approx en la tabla de decisión, como pide la tarea para los decimales (por ejemplo,
la fila de 100.000,50).

## 3. Romper el código a propósito


Hice cuatro cambios a mano en VS Code, uno a la vez. Después de cada cambio guardé,
corrí pytest y anoté qué pasó. Luego deshice el cambio con git restore y revisé con
git status que el código quedara como estaba. Antes de empezar pasaban las 35 pruebas
y al terminar volvieron a pasar las 35.

| Cambio introducido | Archivo y línea | ¿Alguna prueba falló? | Qué hice |
|---|---|---|---|
| Cambié <= por < en la validación de la fecha | deudas.py, línea 10 | Sí, 1: test_fecha_de_hoy_o_anterior_da_error con la fecha de hoy | Nada. Con el cambio se aceptaba una deuda que vence hoy, y la prueba del límite "hoy" lo detectó. |
| Cambié el mínimo de transacciones de 5 a 4 | recomendaciones.py, línea 3 | Sí, 1: test_pocas_transacciones_da_error con 4 transacciones | Nada. Lo detectó el caso límite de 4 transacciones. |
| Hice que la función devolviera siempre 0 | recomendaciones.py, línea 22 | Sí, 4: tres filas de la tabla de decisión (100.001, 120.000 y 100.000,50) y la prueba con los gastos del mes | Nada. Fallaron todas las pruebas que esperan un recorte mayor que 0. |
| Cambié > por >= en la comparación con el tope | recomendaciones.py, línea 21 | No, pasaron las 35 | No agregué prueba. Explico por qué abajo. |

Sobre el último cambio: solo afecta el caso en que el gasto en ocio es igual al tope.
Con un gasto de 100.000 y un tope de 100.000, el código original devuelve 0 porque
100.000 no es mayor que 100.000. El código cambiado entra al if, pero devuelve
100.000 - 100.000, que también es 0. Como las dos versiones dan el mismo resultado
con cualquier dato, ninguna prueba puede notar la diferencia. A esto se le llama un
mutante equivalente. No es que falte una prueba: la fila de 100.000 sí revisa ese
borde, y las dos versiones cumplen la regla de HU-02, porque llegar justo al tope
no es superarlo.

También encontré un error real antes de romper el código a propósito. Al escribir las
pruebas de recomendaciones.py fallaron 4, porque la función devolvía 0 cuando tenía
que devolver un recorte. Primero revisé la función y estaba bien. El error estaba en
test_recomendaciones.py: escribí el tope con un cero de más (1.000.000 en vez de
100.000). La regla de HU-02 dice que el tope es de $100.000, así que corregí el número.
No cambié la prueba para que pasara, la corregí para que dijera lo mismo que la regla.


## 4. Datos de prueba

Los datos de prueba están en tests/conftest.py, en el fixture gastos_del_mes. Son
nueve gastos de un mes de una persona inventada que vive en Neiva. La lista la
propuso la IA y yo la escribí en el archivo. Revisé a mano la suma de los gastos de
ocio (45.000 + 32.000 + 26.900 + 18.000 = 121.900), que es el número que usa la
prueba test_con_los_gastos_del_mes.

No hay datos de personas reales: no hay nombres, cédulas, correos ni teléfonos.
El modelo de datos del proyecto no tiene campo de teléfono, por eso no se incluyeron.
El único nombre de negocio, D'Alirio, es inventado.

Para que tuvieran contexto local usé gastos comunes en Neiva, como el almuerzo
corriente, las achiras en el terminal, el tejo y el mototaxi.

Casos difíciles que incluí a propósito:

- Tildes y ñ: "Piñata para el cumpleaños de la sobrina", "Suscripción de streaming".
- Apóstrofo: "Tejo en D'Alirio".
- Texto vacío: un gasto de transporte sin concepto.
- Monto en cero: "Mototaxi de cortesía", que no cobró nada.

La función tiene que funcionar con todos estos casos. Por ejemplo, el gasto sin
concepto y el de monto cero cuentan para el mínimo de 5 transacciones, pero no
cambian la suma del ocio porque son de transporte.
