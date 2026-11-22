# Registro de pruebas: tabla de casos y pruebas de la IA

Proyecto: SmartFinance AI
Estudiante: Nicolás Andrés Gutiérrez Collazos
Fecha: 2026-11-22

Funciones probadas: cinco con reglas de negocio (cálculo, validación, estados) y dos que
combinan condiciones con tabla de decisión: `generar_alerta_vencimiento` y
`evaluar_gasto_ocio`. Total: **76 pruebas** con `pytest -v`, todas en verde. Las 15 de
`tests/test_presupuesto.py` (semanas 5 y 6) no se tocaron.

Los nombres de las pruebas se abrevian así: `fecha_no_posterior[hoy]` es
`tests/test_deudas.py::test_fecha_no_posterior_a_hoy_se_rechaza[hoy]`.

## 1. Tabla de casos

### Regla 1: `calcular_limite_diario` (HU-04)

**Regla completa (el oráculo):** HU-04: «Dado que el usuario fija una meta de ahorro de
$300.000 COP para un mes de 30 días, con ingresos de $1.500.000 COP, entonces asigna un
margen máximo de gasto de $40.000 COP diarios». Escenario 2: «La meta supera tu
disponibilidad mensual ($100.000 COP máximo)». HU-07, escenario 2: el valor debe ser un
monto positivo. La fórmula acordada en la semana 5: (ingresos − gastos fijos − meta −
gastado) ÷ días que faltan contando hoy, en pesos enteros hacia abajo, nunca negativo. Un
mes tiene de 28 a 31 días.

Particiones y límites nuevos (en `tests/test_presupuesto_tabla.py`). Los casos que ya
cubrían las 15 pruebas anteriores no se repiten; se citan con su nombre.

| Técnica | Partición o límite | Entrada (sobre ingresos 3.000.000, mes de 30) | Esperado | Prueba que lo cubre |
|---|---|---|---|---|
| Partición válida | Caso normal de la historia | 1.500.000, meta 300.000, 30 días | 40.000 | `test_escenario_de_la_historia_da_cuarenta_mil_diarios` (S5) |
| Límite | Último inválido por debajo | dias_del_mes 27 | ValueError | `limites[mes-27]` |
| Límite | Primer válido | dias_del_mes 28 | 107.142 | `limites_validos[mes-28]` |
| Límite | Último válido | dias_del_mes 31 | 96.774 | `limites_validos[mes-31]` |
| Límite | Primer inválido por encima | dias_del_mes 32 | ValueError | `limites[mes-32]` |
| Límite | Día anterior al primero | dia_actual 0 | ValueError | `limites[dia-0]` |
| Límite | Primer día | dia_actual 1 | 100.000 | `limites_validos[dia-1]` |
| Límite | Día después del último | dia 31 en mes de 30 | ValueError | `test_un_dia_que_no_existe_en_ese_mes_se_rechaza` (S5) |
| Límite | Meta igual a lo disponible | fijos 400.000, meta 600.000 (sobre 1.000.000) | 0 | `test_meta_igual_a_la_disponibilidad_deja_el_cupo_en_cero` (S5) |
| Límite | Meta un peso por encima | fijos 400.000, meta 2.600.001 | MetaInalcanzableError | `limites[meta-mas-1]` |
| Límite | Fijos iguales a ingresos | fijos 3.000.000 | 0 | `limites_validos[fijos-igual-ingresos]` |
| Límite | Fijos un peso por encima | fijos 3.000.001 | GastosSuperanIngresosError | `limites[fijos-mas-1]` |
| Límite | Gastado igual al saldo | día 30, gastado 3.000.000 | 0 | `limites_validos[gastado-igual-saldo]` |
| Límite | Un peso antes del borde | día 30, gastado 2.999.999 | 1 | `limites_validos[gastado-un-peso-menos]` |
| Partición válida | Todo en cero | ingresos 0 | 0 | `limites_validos[ingresos-cero]` |
| Partición inválida | Monto negativo (cada uno) | ingresos, fijos o gastado en −1 | MontoInvalidoError | `limites[ingresos-negativos]`, `[fijos-negativos]`, `[gastado-negativo]` |
| Partición inválida | Monto de tipo texto | meta "300000" | MontoInvalidoError | `limites[meta-texto]` |
| Partición inválida | Días con decimales | dias_del_mes 30.0 | ValueError | `limites[dias-float]` |

**Ambigüedades encontradas:** Ninguna nueva. Las de esta regla (si hoy cuenta, redondeo,
negativos) se resolvieron en la semana 5 y están en la bitácora, entradas 2 a 4.

### Regla 2: `validar_fecha_vencimiento` (HU-03, escenario 2)

**Regla completa (el oráculo):** «Dado que el usuario intenta registrar una deuda con
vencimiento el 10 de octubre de 2026 y hoy es 2 de noviembre de 2026, cuando presiona
guardar, entonces el sistema muestra "La fecha de vencimiento debe ser posterior a la fecha
actual"».

| Técnica | Partición o límite | Entrada (hoy = 13/11/2026) | Esperado | Prueba que lo cubre |
|---|---|---|---|---|
| Partición inválida | Fecha pasada (escenario tal cual) | 10/10/2026 con hoy 02/11/2026 | FechaVencimientoInvalidaError | `fecha_no_posterior[escenario-HU03]` |
| Límite | Último día pasado | 12/11/2026 | FechaVencimientoInvalidaError | `fecha_no_posterior[ayer]` |
| Límite | Hoy (A-01) | 13/11/2026 | FechaVencimientoInvalidaError | `fecha_no_posterior[hoy]` |
| Límite | Primer día válido | 14/11/2026 | Acepta (None) | `fecha_posterior[manana]` |
| Partición válida | Futura lejana | 13/11/2027 | Acepta (None) | `fecha_posterior[dentro-de-un-anio]` |
| Partición inválida | Texto, fecha con hora, nada | "2026-11-15", datetime, None | TypeError | `fecha_de_tipo_invalido[texto]`, `[datetime]`, `[none]` |

**Ambigüedades encontradas:** A-01. ¿Vencer hoy es «posterior a la fecha actual»?
**Decisión:** no. «Posterior» es estricto, y una deuda que vence hoy ya no se puede
registrar a tiempo para un aviso. Pendiente de confirmar con el docente.

### Regla 3: `generar_alerta_vencimiento` (HU-03, escenario 1). Combina condiciones.

**Regla completa (el oráculo):** «Dado que la tarjeta de crédito vence el 15 de noviembre
con un saldo de $200.000 COP y hoy es 13 de noviembre, cuando el agente de backend ejecuta
su verificación diaria, entonces envía la alerta "Recordatorio: tu tarjeta de crédito por
$200.000 COP vence en 2 días"». Y HU-06: una deuda pagada ya no es un compromiso.

**Tabla de decisión** (hoy = 13/11/2026, deuda de $200.000):

| Regla | C1: ¿Pendiente? | C2: días que faltan | Acción | Prueba |
|---|---|---|---|---|
| R1 | Sí | 3 o más | Sin alerta (None) | `alerta_tabla[R1-faltan-3]` |
| R2 | Sí | 2 | «… vence en 2 días» | `alerta_tabla[R2-faltan-2]` |
| R3 | Sí | 1 | «… vence en 1 día» | `alerta_tabla[R3-falta-1]` |
| R4 | Sí | 0 | «… vence hoy» | `alerta_tabla[R4-hoy]` |
| R5 | Sí | Negativo (vencida) | Sin alerta (None) | `alerta_tabla[R5-vencida]` |
| R6 | No (Pagado) | Cualquiera (no importa) | Sin alerta (None) | `alerta_tabla[R6-pagada]` |

R6 está simplificada: si la deuda está pagada, los días no importan, así que las cinco
combinaciones de «Pagado» se reducen a una fila.

| Técnica | Partición o límite | Entrada | Esperado | Prueba que lo cubre |
|---|---|---|---|---|
| Límite | Primer día fuera de la ventana | faltan 3 | None | `alerta_tabla[R1-faltan-3]` |
| Límite | Primer día dentro | faltan 2 | Mensaje exacto | `alerta_tabla[R2-faltan-2]` |
| Límite | Último día dentro | faltan 0 | «vence hoy» | `alerta_tabla[R4-hoy]` |
| Límite | Primer día después | faltan −1 | None | `alerta_tabla[R5-vencida]` |
| Partición válida | Datos con ñ y espacios sobrantes | Cooperativa Ñambú, faltan 2 | Mensaje con ñ y sin espacios | `test_alerta_con_datos_sinteticos_recorta_espacios_y_conserva_la_enie` |
| Partición inválida | Estado escrito como texto | estado "Pagado" | ValueError | `test_estado_escrito_como_texto_se_rechaza` |

**Ambigüedades encontradas:**
- A-02. El escenario solo muestra el aviso a 2 días. ¿Sale solo ese día o también a 1 día
  y el mismo día? **Decisión:** desde 2 días antes hasta el día del vencimiento, porque
  el cliente dijo «se me pasan las fechas»; un solo aviso se pierde fácil. En singular
  «1 día» y «vence hoy» para el día 0. Se relaciona con la pregunta abierta P-02.
- A-03. ¿Una deuda vencida y sin pagar genera la alerta? **Decisión:** no; la historia
  habla de un aviso preventivo. El aviso de mora queda como pregunta para el cliente.

### Regla 4: `marcar_como_pagada` y `total_pendiente` (HU-06), y el registro de una `Deuda`

**Regla completa (el oráculo):** «Dado que la deuda "Servicio de Internet" por $80.000 COP
figura como pendiente, cuando el usuario elige "Marcar como pagado", entonces el estado
cambia a "Pagado" y el monto se descuenta del total de compromisos del mes». Escenario 2:
si ya figura como pagada, «Esta deuda ya ha sido saldada previamente». Modelo de datos:
una deuda tiene acreedor, monto_total, fecha_vencimiento y estado (Pendiente o Pagado).

| Técnica | Partición o límite | Entrada | Esperado | Prueba que lo cubre |
|---|---|---|---|---|
| Partición válida | Pendiente → Pagado | Internet $80.000 pendiente | Estado Pagado; acreedor y monto iguales; la original sigue pendiente | `test_marcar_como_pagada_cambia_solo_el_estado` |
| Partición inválida | Ya pagada | Internet $80.000 pagada | DeudaYaPagadaError con el texto exacto | `test_pagar_dos_veces_lanza_deuda_ya_pagada` |
| Partición válida | Mezcla de estados | 5 deudas sintéticas | 630.000 | `test_total_pendiente_suma_solo_las_pendientes` |
| Partición válida | Después de pagar una | Pagar Internet | 630.000 − 80.000 = 550.000 | `test_pagar_una_deuda_la_descuenta_del_total` |
| Límite | Lista vacía | [] | 0 | `test_total_pendiente_sin_deudas_es_cero` |
| Límite | Monto cero (A-07) | natillera $0 | Se acepta | `test_deuda_en_cero_es_valida` |
| Partición inválida | Monto negativo o float | −1, 80000.0 | MontoInvalidoError | `test_monto_de_deuda_invalido_lanza_monto_invalido[negativo]`, `[float]` |
| Partición inválida | Acreedor vacío | "", "   " | ValueError | `test_acreedor_vacio_se_rechaza[vacio]`, `[solo-espacios]` |

**Ambigüedades encontradas:** A-07. ¿Una deuda de $0 es válida? La regla de HU-07 dice
«monto positivo», pero es para la meta de ahorro, no para deudas. **Decisión:** se acepta
cero (no negativo), porque una cuota ya abonada completa existe y no debe romper el total.

### Regla 5: `evaluar_gasto_ocio` (HU-02). Combina condiciones.

**Regla completa (el oráculo):** Escenario 1: «Dado que el usuario acumula $120.000 COP en
entretenimiento y su tope mensual es $100.000 COP, cuando la IA analiza el patrón de
consumo, entonces genera la recomendación "Has superado tu límite de ocio; te recomendamos
reducir $30.000 COP en suscripciones secundarias este mes"». Escenario 2: «Dado que el
usuario es nuevo y solo tiene 2 transacciones registradas, entonces el sistema responde
"Se requieren al menos 5 transacciones registradas para generar sugerencias
personalizadas"».

**Tabla de decisión** (tope de ocio $100.000):

| Regla | C0: ¿Tope válido? | C1: ¿5 o más transacciones? | C2: ¿Ocio mayor que el tope? | Acción | Prueba |
|---|---|---|---|---|---|
| R0 | No | No importa | No importa | MontoInvalidoError | `test_el_tope_invalido_se_revisa_antes_que_el_historial` |
| R1 | Sí | No | No importa | HistorialInsuficienteError | `ocio_tabla[R1-2-trx]`, `[R1-4-trx]` |
| R2 | Sí | Sí | No | Sin recomendación (None) | `ocio_tabla[R2-debajo]`, `[R2-igual]` |
| R3 | Sí | Sí | Sí | Recomienda reducir el exceso | `ocio_tabla[R3-un-peso]`, `[R3-escenario-HU02]` |

Tres condiciones dan 8 combinaciones; se simplifican a 4 porque cuando C0 falla no
importan C1 ni C2, y cuando C1 falla no importa C2.

| Técnica | Partición o límite | Entrada | Esperado | Prueba que lo cubre |
|---|---|---|---|---|
| Partición inválida | Sin transacciones | [] | HistorialInsuficienteError | `test_sin_transacciones_es_historial_insuficiente` |
| Partición inválida | Escenario 2 tal cual | 2 transacciones | HistorialInsuficienteError con texto exacto | `ocio_tabla[R1-2-trx]` |
| Límite | Último insuficiente | 4 transacciones | HistorialInsuficienteError | `ocio_tabla[R1-4-trx]` |
| Límite | Primero suficiente, un peso debajo | 5 transacciones, ocio 99.999 | None | `ocio_tabla[R2-debajo]` |
| Límite | Igual al tope (A-05) | ocio 100.000 | None | `ocio_tabla[R2-igual]` |
| Límite | Un peso encima | ocio 100.001 | «reducir $1» | `ocio_tabla[R3-un-peso]` |
| Partición válida | Escenario 1 (A-04) | ocio 120.000 | «reducir $20.000» | `ocio_tabla[R3-escenario-HU02]` |
| Límite | Centavos de exceso | ocio 100.000,01 | «reducir $1» | `bordes_del_monto[centavos]` |
| Límite | Tope cero sin ocio | ocio 0, tope 0 | None | `bordes_del_monto[tope-cero]` |
| Partición válida | Solo «Ocio» suma (A-06) | 1.200.000 en otras, 150.000 en «ocio» minúscula | None | `test_solo_la_categoria_ocio_suma_para_el_tope` |
| Partición válida | Datos sintéticos del mes | 9 transacciones, ocio 121.900 | «reducir $21.900» | `test_con_datos_sinteticos_del_mes` |
| Partición inválida | Monto de transacción inválido | −5000, 5000.0, True | MontoInvalidoError | `transaccion_monto_invalido[negativo]`, `[float]`, `[bool]` |
| Partición inválida | Texto inválido | concepto None, categoría "" o "   " | ValueError | `transaccion_texto_invalido[...]` |

**Ambigüedades encontradas:**
- A-04. **La más importante.** El escenario 1 pide reducir **$30.000** cuando el exceso es
  **$20.000** ($120.000 − $100.000). Con los datos del escenario no hay forma de llegar a
  $30.000: parece copiado del ejemplo de Camila de la semana 1 (dos suscripciones de
  $15.000), que es otra situación. **Decisión:** recomendar reducir exactamente el exceso,
  redondeado hacia arriba al peso, porque es lo mínimo que devuelve al usuario a su tope y
  sale de una cuenta, no de un número suelto. Queda pendiente confirmarlo con el docente y
  corregir el Gherkin del documento de requisitos.
- A-05. ¿Gastar exactamente el tope es «superarlo»? **Decisión:** no; superar es estrictamente mayor.
- A-06. ¿Cuentan para el mínimo de 5 las transacciones de cualquier categoría?
  **Decisión:** sí; la regla dice «transacciones registradas», sin filtro. Para el tope
  solo suma la categoría «Ocio» escrita así; poner en orden «ocio», «OCIO» o «Ócio» le
  toca al clasificador de HU-01.

## 2. Pruebas de la IA descartadas o corregidas

**Prompt usado:** «Eres un tester de Python. Con estas reglas y estas tablas de casos
[se pegaron las secciones de la regla 1 a la 5], escribe pruebas con pytest para
`deudas.py`, `recomendaciones.py` y los límites de `calcular_limite_diario`. Usa
`@pytest.mark.parametrize` con un comentario por fila, `pytest.approx` para decimales,
`pytest.raises` con el tipo de error exacto y esperados fijos. No modifiques el código».
Ver bitácora, entrada 13. El borrador quedó en el commit
`Borrador de pruebas generado por IA, sin revisar`: 25 pruebas nuevas, 3 en rojo.

| Prueba generada | Decisión | Por qué | En su lugar |
|---|---|---|---|
| `test_fecha_hoy_es_valida`: esperaba que vencer hoy no diera error | Corregida | **El esperado no sale de la regla.** Falló, y antes de tocarla se releyó la regla: «posterior» es estricto (A-01). | Fila `fecha_no_posterior[hoy]`: espera FechaVencimientoInvalidaError |
| `test_deuda_con_monto_cero_lanza_error` | Descartada | **Regla inventada.** Tomó «monto positivo» de HU-07, que habla de la meta de ahorro, y la aplicó a las deudas. | `test_deuda_en_cero_es_valida` (A-07) |
| `test_escenario_gherkin_recomienda_reducir`: esperaba $30.000 | Corregida | **El esperado no sale de la regla revisada.** Copió el número del Gherkin sin hacer la cuenta; la tabla ya había resuelto A-04. | `ocio_tabla[R3-escenario-HU02]` con $20.000 |
| `test_alerta_dos_dias_antes`: `assert alerta is not None` | Corregida | **Débil.** Pasaba con cualquier texto, incluso con un monto o un número de días equivocado. | Compara el mensaje exacto del Gherkin: `alerta_tabla[R2-faltan-2]` |
| `test_sin_alerta_si_falta_mucho[faltan 7 días]` | Descartada | **Redundante.** Misma partición que «faltan 3», que además es el límite. | Solo queda `alerta_tabla[R1-faltan-3]` |
| Faltaban 1 día, el mismo día, vencida y estado inválido | Agregadas | La tabla de decisión tenía 6 filas y el borrador cubría 3. | `alerta_tabla[R3]`, `[R4]`, `[R5]` |
| `test_marcar_como_pagada_devuelve_deuda`: `isinstance(…, Deuda)` | Corregida | **Débil.** Pasaba aunque devolviera la deuda sin cambiar (se confirmó con M6). | Revisa estado, acreedor, monto y que la original siga pendiente |
| `test_pagar_dos_veces_lanza_error` | Corregida | Revisaba el tipo pero no el mensaje, que es parte de la regla. | Agrega `match=` con el texto exacto |
| `test_total_pendiente`: el esperado se calculaba con un `sum(...)` igual al del código | Corregida | **El esperado salía del código.** Si el filtro estuviera mal en los dos lados, la prueba pasaría igual. | Esperado fijo 630.000, calculado a mano |
| `test_historial_insuficiente`: `pytest.raises(ValueError)` | Corregida | **Débil.** MontoInvalidoError también es un ValueError, así que pasaba con el error equivocado. | `HistorialInsuficienteError` y el texto exacto |
| `test_sin_recomendacion_si_no_supera[50.000]` y `[80.000]` | Descartadas | **Redundantes** con 99.999: misma partición, y 99.999 además es el límite. | Queda 99.999 (límite); se agrega 100.000 (A-05) y 100.001 |
| `test_con_datos_sinteticos`: `assert evaluar_gasto_ocio(...)` | Corregida | **Débil.** Cualquier texto no vacío la hacía pasar. | Mensaje exacto con $21.900, calculado a mano |
| `test_limite_valido` con `pytest.approx` | Corregida | El prompt pidió `approx` para decimales, pero aquí los montos son `Decimal` exactos en pesos, no `float`. `approx` deja pasar diferencias pequeñas que en plata sí importan. | Igualdad exacta con `==` |
| `test_limite_valido[meta = disponible]` | Descartada | **Redundante** con `test_meta_igual_a_la_disponibilidad_deja_el_cupo_en_cero` (S5). | Se cita esa prueba en la tabla |
| `test_dias_fuera_de_rango`: `pytest.raises(ValueError)` | Corregida | `pytest.raises` acepta subclases: no distingue ValueError de MontoInvalidoError. | `assert excinfo.type is error` |
| `test_fecha_pasada_lanza_error`, `test_fecha_futura_es_valida`, `test_sin_alerta_si_falta_mucho[faltan 3]`, `test_deuda_pagada_no_genera_alerta`, `test_sin_recomendacion_si_no_supera[99.999]`, `test_meta_un_peso_mayor_que_disponible` | Conservadas | El esperado sale de la regla, fallan si se rompe el código y cubren algo único. | Se pasaron a la tabla parametrizada con su comentario |

**Resumen:** la mayoría de las pruebas del borrador corrían, pero muchas comprobaban
poco: cuatro asserts débiles, un error sin su mensaje, dos errores capturados sin tipo
exacto, un esperado copiado del propio código y cuatro casos redundantes. Además faltaban límites, tipos inválidos y la
mitad de las filas de las tablas de decisión, que se agregaron hasta llegar a 61 pruebas
nuevas. Ninguna prueba se ajustó al código: los 3 fallos del borrador se resolvieron
releyendo la regla.

## 3. Romper el código a propósito

Cada cambio se hizo solo, se corrió `pytest`, y se deshizo con `git restore <archivo>`.

| Cambio introducido | Archivo y línea | ¿Alguna prueba falló? | Qué hice |
|---|---|---|---|
| M1: `<= DIAS_DE_AVISO` por `< DIAS_DE_AVISO` | `deudas.py:132` | Sí, 2: `alerta_tabla[R2-faltan-2]` y la de datos sintéticos | Nada: el borde está protegido |
| M2: `fecha_vencimiento <= hoy` por `<` | `deudas.py:101` | Sí, 1: `fecha_no_posterior[hoy]` | Nada: es el caso de A-01 |
| M3: `gasto_ocio <= tope` por `<` | `recomendaciones.py:97` | Sí, 2: `ocio_tabla[R2-igual]` y `bordes_del_monto[tope-cero]` | Nada |
| M4: mínimo de transacciones 5 por 4 | `recomendaciones.py:22` | Sí, 3: `[R1-2-trx]`, `[R1-4-trx]` y la lista vacía (el mensaje dice 4) | Nada |
| M5: redondeo `ROUND_CEILING` por `ROUND_FLOOR` | `recomendaciones.py:101` | Sí, 4: incluida `bordes_del_monto[centavos]`, que pedía $1 y recibió $0 | Nada |
| M6: `marcar_como_pagada` devuelve siempre la misma deuda | `deudas.py:166` | Sí, 2. **El borrador de la IA no lo habría atrapado** (solo revisaba el tipo) | Confirma la corrección de la sección 2 |
| M7: `total_pendiente` suma también las pagadas | `deudas.py:179` | Sí, 2: total y descuento tras pagar | Nada |
| M8: `+ 1` por `+ 2` en los días restantes | `presupuesto.py:164` | Sí, 11, entre ellas el escenario de HU-04 | Nada |
| M9: quitar la validación de que el concepto sea texto | `recomendaciones.py:51` | **No. 72 en verde** | Agregué `transaccion_texto_invalido[concepto-none]`; repetí M9 y falló |
| M10: quitar la validación del estado de la deuda | `deudas.py:80` | **No. 72 en verde** | Agregué `test_estado_escrito_como_texto_se_rechaza`. Era grave: «Pagado» como texto pasaba como pendiente y generaba alerta |
| M11: quitar la validación de categoría vacía | `recomendaciones.py:53` | Mismo patrón que M9, así que agregué los casos antes de probar; con ellos, sí: 2 | Agregué `[categoria-vacia]` y `[categoria-espacios]` |

**Lección de proceso.** La primera ronda dio resultados falsos: M2 fallaba en las mismas
pruebas que M1, y M9 y M10 rompían pruebas del presupuesto que no tenían relación. La causa
fue la caché de Python (`__pycache__`): el cambio y el `git restore` ocurrían en el mismo
segundo y con el mismo tamaño de archivo, y Python siguió usando la versión rota ya
compilada. Se repitió todo con `PYTHONDONTWRITEBYTECODE=1`, borrando `__pycache__` y con
`pytest -p no:cacheprovider`. La tabla de arriba es la de esa segunda ronda.

## 4. Datos de prueba

**Origen:** sintéticos, generados con IA (Claude) y revisados a mano; están en los
fixtures `transacciones_sinteticas` y `deudas_sinteticas` de `tests/conftest.py`.
Confirmo que no hay datos de personas reales: la persona es inventada, los negocios
(«D'Alirio», «D'Toño», «Cooperativa Ñambú») son inventados y no hay nombres, cédulas,
correos ni cuentas. No hay teléfonos porque el modelo de datos de la semana 4 no tiene ese
campo; agregarlos habría sido un dato inventado que ninguna prueba usa.

**Contexto local:** gastos de un mes en Neiva: almuerzo corriente en el centro, achiras en
el terminal, tejo con compañeros, mototaxi, mercado; deudas en pesos colombianos
(tarjeta, Internet, cuota de la moto, fiado en la tienda, natillera).

**Casos difíciles incluidos:** tildes y ñ («Piñata… cumpleaños», «Cooperativa Ñambú»),
apóstrofo («D'Alirio», «D'Toño»), texto vacío (concepto «»), espacios sobrantes al inicio
y al final del acreedor, monto en cero (mototaxi de cortesía, natillera abonada), una deuda
ya pagada mezclada con pendientes, y centavos ($100.000,01, en las pruebas de borde).

**Revisión de los datos de la IA:** se revisó fila por fila que ningún nombre fuera de
una persona o de una empresa conocida («cine» y «streaming» quedaron genéricos, sin marca).
Las sumas que usan las pruebas (ocio $121.900, pendientes $630.000) se hicieron a mano y
están escritas en el docstring de cada fixture; las pruebas fijan esos números, no los
recalculan.
