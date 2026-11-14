# Bitácora de uso de IA

Proyecto: SmartFinance AI
Estudiante: Nicolás Andrés Gutiérrez Collazos
Funcionalidad: HU-04 Calcular el límite de gasto diario según la meta de ahorro
Asistente usado: Claude (modo chat y agente, trabajando sobre el repositorio)

## Entradas

### Entrada 1

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** «De mis historias Must (HU-01 a HU-04), ¿cuál sirve mejor para
  una funcionalidad pequeña con casos límite?». El asistente propuso HU-04 en lugar de
  HU-01, que era la candidata obvia por ser la historia estrella del proyecto.
- **Decisión:** Aceptada
- **Por qué:** HU-01 depende de la API del modelo de lenguaje. Para probarla habría que
  simular esa API, y una prueba que depende de un servicio externo no da el mismo
  resultado siempre. HU-04 es una cuenta matemática: no toca red ni base de datos.
- **Verificación:** Las 11 pruebas corren con `pytest` sin conexión a internet y dan el
  mismo resultado en cada ejecución.
- **Commit relacionado:** `Pruebas del limite de gasto diario (en rojo)`

### Entrada 2

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** El asistente propuso ampliar la firma de la función con dos
  parámetros que no estaban en el criterio de aceptación: `dia_actual` y
  `gastado_hasta_hoy`.
- **Decisión:** Aceptada con cambios
- **Por qué:** Sin el día actual la función solo sirve el día 1 del mes, y HU-07 pide
  poder recalcular a mitad de periodo. Acepté los dos parámetros, pero les puse valor por
  defecto (día 1 y cero gastado) para que el escenario 1 de HU-04 siga funcionando con
  tres argumentos, tal como lo describe el criterio de aceptación.
- **Verificación:** La prueba `test_escenario_de_la_historia_da_cuarenta_mil_diarios`
  llama la función sin esos dos parámetros y pasa; la prueba
  `test_a_mitad_de_mes_reparte_solo_el_saldo_entre_los_dias_que_faltan` sí los usa.
- **Commit relacionado:** `Pruebas del limite de gasto diario (en rojo)`

### Entrada 3

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** El asistente devolvía la división tal cual, `saldo / dias`, que
  en `Decimal` redondea al valor par más cercano. Con un saldo de $100 en 3 días eso da
  $33,33 y, según el caso, puede subir a $34.
- **Decisión:** Aceptada con cambios
- **Por qué:** Redondear hacia arriba le da permiso al usuario de gastar más de lo que
  debería y, al final del mes, de no cumplir la meta por unos pesos. En una app de ahorro
  el error tiene que caer siempre del lado seguro. Cambié el cálculo a `ROUND_FLOOR`.
- **Verificación:** Escribí `test_redondea_hacia_abajo_para_no_romper_la_meta`, que exige
  $33 y falla si el resultado es $34.
- **Commit relacionado:** `Implementa calcular_limite_diario: pruebas en verde`

### Entrada 4

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** La primera versión devolvía el resultado de la resta aunque
  fuera negativo, es decir, un cupo diario en rojo cuando la persona ya se había pasado.
- **Decisión:** Rechazada
- **Por qué:** «Puedes gastar -$4.166 diarios» no es información que alguien pueda usar.
  Lo útil es decir cero y que el usuario entienda que por este mes ya no hay margen.
  Cambié la resta por un `max(CERO, ...)`.
- **Verificación:** `test_si_ya_se_paso_del_presupuesto_devuelve_cero_y_no_un_negativo`
  exige exactamente `Decimal("0")`.
- **Commit relacionado:** `Implementa calcular_limite_diario: pruebas en verde`

### Entrada 5

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** El asistente propuso convertir en prueba el ejemplo de Camila
  que está en mi propuesta de la semana 1, usando el valor de $9.100 diarios que aparece
  escrito allí.
- **Decisión:** Rechazada
- **Por qué:** Al hacer la cuenta a mano el número no daba. Quedan $110.000 repartidos en
  12 días, que son $9.166,67, no $9.100. El error estaba en mi propio documento, donde
  había redondeado mal. Una prueba con el número equivocado habría dejado el error fijo
  en el código.
- **Verificación:** La prueba con $9.166 pasa y con $9.100 falla. Corregí también el
  documento de la propuesta para que diga $9.166 y $11.666.
- **Commit relacionado:** `Pruebas del limite de gasto diario (en rojo)`

### Entrada 6

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** Como alternativa a pasar `dia_actual` como parámetro, el
  asistente planteó leer la fecha dentro de la función con `date.today()`, para que quien
  la llama no tenga que pasarla.
- **Decisión:** Rechazada
- **Por qué:** Una función que lee el reloj devuelve algo distinto cada día, así que las
  pruebas dejarían de ser repetibles: la misma prueba pasaría hoy y fallaría mañana.
  Prefiero que la fecha entre como dato y que quien llame a la función decida de dónde
  sacarla.
- **Verificación:** Con el día como parámetro, las 11 pruebas dan el mismo resultado sin
  importar cuándo se ejecuten.
- **Commit relacionado:** `Pruebas del limite de gasto diario (en rojo)`

### Entrada 7

- **Fecha:** 2026-11-07
- **Prompt o sugerencia:** «Con las pruebas en verde, propón un refactor». El asistente
  sugirió sacar las validaciones a funciones aparte, reemplazar los números 28 y 31 por
  constantes con nombre y mover el formato de pesos a su propia función.
- **Decisión:** Aceptada
- **Por qué:** La función principal tenía cuatro `if` casi idénticos revisando montos
  negativos y dos números sueltos que no explicaban nada. Después del refactor la función
  pasó de 50 a 20 líneas y se leen los tres pasos del contrato de corrido.
- **Verificación:** Las 11 pruebas siguen pasando y `git diff` sobre la carpeta `tests/`
  sale vacío, así que no se tocó ninguna.
- **Commit relacionado:** `Refactor: saca las validaciones y los valores magicos de la funcion`

---

## Entradas de la semana 6 (revisión de código y seguridad)

### Entrada 8

- **Fecha:** 2026-11-14
- **Prompt o sugerencia:** Segunda revisión con IA. Prompt: «Revisa `presupuesto.py` y
  `test_presupuesto.py` con estos criterios: corrección frente al contrato, casos límite,
  seguridad (OWASP), legibilidad y mantenibilidad. Entrega una tabla con archivo y línea,
  problema, categoría y severidad. Separa los problemas seguros de las sospechas. No
  propongas cambios a las pruebas». El asistente devolvió 8 hallazgos: 3 seguros y 5
  sospechas.
- **Decisión:** Aceptada con cambios
- **Por qué:** Acepté los 4 hallazgos que resultaron reales (dos docstrings incompletos,
  una guarda repetida y un mensaje que dice «positivo» aunque acepta cero) y descarté los
  4 falsos positivos. El más llamativo fue «posible división por cero»: suena grave, pero
  la validación del día hace imposible que los días restantes sean cero.
- **Verificación:** Cada hallazgo se buscó en el código por número de línea. La división
  por cero se comprobó leyendo `_exigir_que_el_dia_exista` y con la prueba del último día
  del mes, que da 1 día y no 0. El detalle de los 8 está en `revision_seguridad.md`,
  sección 3.
- **Commit relacionado:** `34e0f35` (informe) y `11c8723` (docstrings)

### Entrada 9

- **Fecha:** 2026-11-14
- **Prompt o sugerencia:** Para el hallazgo H-02 (gastos fijos mayores que los ingresos
  daban «$-200.000 COP máximo»), el asistente propuso reutilizar `MetaInalcanzableError`
  cambiando solo el texto del mensaje según el caso.
- **Decisión:** Aceptada con cambios
- **Por qué:** Reutilizar la excepción arreglaba el mensaje, pero mezclaba dos situaciones
  distintas bajo el mismo nombre: «tu meta es muy alta» y «tus gastos fijos superan lo que
  ganas». Quien use la función querrá reaccionar distinto a cada una. Creé una excepción
  nueva, `GastosSuperanIngresosError`, que dice las dos cifras.
- **Verificación:** Prueba nueva `test_gastos_fijos_mayores_que_los_ingresos_avisan_claro`,
  que exige que el mensaje traiga los dos montos y no traiga ningún «$-». Las 11 pruebas
  anteriores no se tocaron.
- **Commit relacionado:** `6789feb`

### Entrada 10

- **Fecha:** 2026-11-14
- **Prompt o sugerencia:** En la revisión, el asistente señaló que seis parámetros son
  demasiados y propuso agruparlos en una `dataclass` llamada `DatosDelMes`.
- **Decisión:** Rechazada (pospuesta)
- **Por qué:** La observación es válida en abstracto, pero hoy todas las llamadas usan
  nombres (`meta_ahorro=...`) y se leen bien. Y el diseño de la semana 4 ya dice que la
  capa HTTP tendrá un modelo de Pydantic para `POST /api/v1/metas-ahorro`; ese modelo va
  a ser exactamente el agrupador que la IA propone. Hacer una dataclass ahora sería
  construir dos veces lo mismo.
- **Verificación:** Revisé que ninguna llamada en las 15 pruebas use argumentos por
  posición más allá de los cuatro obligatorios. Quedó anotado en la tabla de pendientes
  del informe, con el plan.
- **Commit relacionado:** `34e0f35` (sección 4 del informe)

### Entrada 11

- **Fecha:** 2026-11-14
- **Prompt o sugerencia:** Trabajo del agente de código. Instrucción delimitada: «Trabaja en
  la rama `revision-semana-6`. Configura ruff, corrige cada hallazgo en su propio commit
  con un mensaje que diga qué se corrigió, no modifiques ninguna prueba existente, agrega
  pruebas nuevas si cambias el comportamiento, no instales dependencias nuevas, y no
  integres a `main`».
- **Decisión:** Aceptada
- **Por qué:** La rama separada permite ver todo el diff antes de integrarlo, que es lo
  que pide la tarea. El agente hizo 9 commits, uno por cambio. Revisé el diff completo
  (`git diff main..revision-semana-6`) antes de integrar: ninguna prueba de la semana 5
  cambió, las 4 nuevas corresponden a los hallazgos, y no entró ninguna dependencia.
- **Verificación:** `ruff check .` sin avisos, `pytest` con 15 en verde, `git diff --stat`
  de `tests/` muestra solo líneas agregadas, ninguna borrada. La integración a `main` se
  hace con `--no-ff`, para que la rama quede visible en el historial.
- **Commit relacionado:** rama `revision-semana-6`, del `8e77108` al último de la rama

## Resumen

| Decisión | Cantidad |
|---|---|
| Aceptadas | 3 |
| Aceptadas con cambios | 4 |
| Rechazadas | 4 |

Semana 5: entradas 1 a 7. Semana 6: entradas 8 a 11.

## Errores que atraparon las pruebas

El error más claro fue el del valor de $9.100 diarios (entrada 5). Al escribir la prueba
del caso de mitad de mes tuve que poner el resultado esperado, y al calcularlo a mano vi
que no coincidía con lo que decía mi propia propuesta. La cuenta correcta es $110.000
entre 12 días, o sea $9.166. Si hubiera escrito el código primero y la prueba después,
probablemente habría ajustado la prueba al resultado que diera el código y el número malo
se habría quedado ahí.

El segundo lo atrapó el escenario 1 de HU-04, que fija un número exacto: $40.000 diarios
con ingresos de $1.500.000, meta de $300.000 y un mes de 30 días. Esa cifra solo sale si
el día de hoy cuenta dentro de los días que faltan. Una implementación que calcule
`dias_del_mes - dia_actual` en vez de `+ 1` reparte entre 29 días y devuelve $41.379, y la
prueba falla de inmediato. Sin ese criterio con números concretos, la decisión de si hoy
cuenta o no se habría quedado como una ambigüedad del contrato.

**Semana 6.** Esta vez los errores no los atrapó una prueba existente sino la revisión, y
por eso se escribieron pruebas nuevas para que no vuelvan. El «máximo negativo» (H-02) no
lo detectó ni el linter ni la lectura: el código era correcto en la forma. Apareció al
ejecutar la función con un caso real, alguien con gastos fijos de $1.000.000 y sueldo de
$800.000. Y el `float` que reventaba con un `TypeError` (H-03) lo encontré probando
«qué pasa si alguien manda el número mal». Las 4 pruebas nuevas dejan los dos casos
clavados.

## Reflexión final

Donde más me ayudó el asistente fue en la velocidad del borrador: la estructura del
repositorio, la primera versión de la función y las propuestas de refactor salieron en
minutos. Escribir las pruebas antes resultó ser la parte más valiosa del ejercicio, y no
por disciplina sino por algo concreto: al tener que escribir el resultado esperado
encontré un error de aritmética que llevaba semanas en mi documento de la propuesta.

Lo que el asistente no hace es decidir. Las tres sugerencias que rechacé no eran código
mal escrito, eran decisiones razonables en abstracto que chocaban con algo de mi proyecto:
el redondeo hacia arriba contra la meta de ahorro, el número negativo contra la utilidad
para el usuario, y la fecha leída del reloj contra la repetibilidad de las pruebas.
Ninguna de esas tres la habría detectado leyendo el código por encima.

Para la próxima funcionalidad cambiaría el orden en que doy el contexto: esta vez le pasé
el contrato y las pruebas juntos, y la primera respuesta mezcló validaciones con lógica de
negocio. Creo que si primero fijo los casos límite y solo después pido la implementación,
el borrador llega más limpio y me ahorro parte del refactor.

**Sobre la semana 6.** Lo que más me sirvió de la segunda revisión no fueron los
hallazgos reales sino los falsos positivos: verificar por qué «división por cero» no puede
pasar me obligó a seguir el flujo de validaciones completo, y ahí entendí mi propio código
mejor que cuando lo escribí. Lo que cambiaría: correr la revisión con IA **antes** de la
manual, no después. Así la lectura humana se concentra en lo que la herramienta no ve,
que esta semana fue justamente lo que importaba.
