# Informe final del proyecto integrador

Proyecto: SmartFinance AI
Estudiante: Nicolás Andrés Gutiérrez Collazos
Repositorio: https://github.com/nicolasgutierrezco-beep/smartfinance-ai
Fecha: 2026-11-27

## 1. Resumen

Las personas que manejan sus finanzas solas dejan de anotar sus gastos porque las apps son
tediosas, y se enteran a fin de mes de que gastaron de más o de que se les pasó una fecha
de pago. SmartFinance AI propone una app que entiende los gastos escritos en frases
normales, calcula cuánto se puede gastar al día y avisa antes de que algo salga mal.
Usé IA en las seis fases del proyecto: Gemini Notebook para la propuesta, los requisitos y
el diseño, y Claude para el código, las pruebas y el pipeline. Hoy están programadas tres
funciones de la lógica de negocio, con 35 pruebas que pasan y un pipeline que las corre en
cada cambio. Al verificar encontré errores de la IA en todas las fases, como un módulo de
criptomonedas que nadie pidió o una prueba que esperaba $30.000 cuando la cuenta daba
$20.000.

## 2. Problema y usuario

El usuario es una persona independiente que maneja sus finanzas personales. Para el
proyecto se trabajó con un cliente simulado que representa a ese tipo de usuario, en una
entrevista simulada de 25 minutos el 1 de noviembre de 2026.

Antes, este usuario anotaba sus gastos a mano en apps que funcionan como un cuaderno:
hay que llenar un formulario y escoger la categoría de una lista. Como es tedioso, deja de
anotar a los pocos días. Y cuando sí anota, la app solo suma, así que se entera de que
gastó de más a fin de mes, cuando ya no puede hacer nada. Además, se le pasan las fechas
de pago de la tarjeta y le cobran intereses.

De la entrevista salieron seis necesidades:

- N-01: registrar gastos sin escoger la categoría en una lista.
- N-02: saber en qué está gastando de más, como streaming o salidas.
- N-03: recibir recordatorios antes de que venzan las deudas.
- N-04: saber cuánto puede gastar al día sin dañar su meta de ahorro.
- N-05: que sus datos financieros estén seguros y no se compartan.
- N-06: que la app responda rápido al registrar un gasto.

Evidencia: la propuesta está en las secciones 2 y 6, y la entrevista con las necesidades
en las secciones 7 y 8 del [documento de las semanas 1 a 4](docs/documento_semanas_1_a_4.pdf).

## 3. La IA en el ciclo de vida

| Módulo y fase | Qué hice con IA | Herramienta | Evidencia (enlace) | Cómo verifiqué |
|---|---|---|---|---|
| 1. Fundamentos | Comparé dos asistentes con el mismo prompt y estructuré la propuesta del proyecto | ChatGPT, Claude y Gemini Notebook | [Documento semanas 1 a 4](docs/documento_semanas_1_a_4.pdf), secciones 1 a 6 | Ejecuté el código de cada asistente para compararlos. En la propuesta concreté el problema con un ejemplo en pesos |
| 2. Requisitos | Organicé las necesidades de la entrevista, redacté 8 historias de usuario con escenarios Gherkin y prioricé con MoSCoW | Gemini Notebook | [Documento semanas 1 a 4](docs/documento_semanas_1_a_4.pdf), secciones 7 a 12 | Revisé cada necesidad contra lo que dijo el cliente e hice a mano la cuenta del porcentaje de historias Must |
| 3. Diseño | Comparé alternativas de arquitectura, escribí el ADR-001, los diagramas C4, el modelo de datos y los endpoints | Gemini Notebook | [Documento semanas 1 a 4](docs/documento_semanas_1_a_4.pdf), secciones 13 en adelante | Revisé que los diagramas coincidieran con el ADR-001 y con los requisitos no funcionales |
| 4. Código | Programé calcular_limite_diario con pruebas primero y revisé el código con un linter y con IA | Claude (chat y Claude Code) | [presupuesto.py](src/smartfinance/presupuesto.py), [revision_seguridad.md](revision_seguridad.md), [bitácora](bitacora_ia.md), entradas 1 a 11 | Corrí las pruebas y ruff, y clasifiqué cada hallazgo de la IA como real o falso positivo |
| 5. Pruebas | Diseñé tablas de casos, generé pruebas y datos sintéticos, y después simplifiqué el código y las pruebas | Claude | [registro_pruebas.md](registro_pruebas.md), [carpeta tests](tests), [bitácora](bitacora_ia.md), entradas 12 a 19 | Revisé las pruebas con las tres preguntas y rompí el código a mano cuatro veces |
| 6. Operación | Agregué un pipeline que corre ruff y pytest cada vez que subo cambios, [plan de operación](docs/plan_operacion.md). | Claude | [pruebas.yml](.github/workflows/pruebas.yml) y la pestaña Actions del repositorio | La primera ejecución del pipeline pasó en verde |

## 4. Verificación: lo que la IA hizo mal y cómo lo encontré

### Caso 1: la IA inventó una funcionalidad que nadie pidió

- **Fase:** requisitos.
- **Qué propuso la IA:** Gemini Notebook sugirió agregar un módulo de compra y venta de
  criptomonedas con trading automático. Además, al priorizar las historias con MoSCoW,
  dejó el 62,5 % como Must.
- **Qué estaba mal:** el cliente nunca pidió nada de criptomonedas; estaba por fuera del
  alcance. Y el 62,5 % pasaba el límite de 60 % de historias Must.
- **Cómo lo detecté:** comparé cada historia con las necesidades de la entrevista y ninguna
  hablaba de inversiones. El porcentaje lo revisé haciendo la cuenta a mano.
- **Qué hice:** descarté el módulo de criptomonedas y pasé una historia de Must a Should,
  con lo que quedó en 50 %. Está en la sección 12 del
  [documento de las semanas 1 a 4](docs/documento_semanas_1_a_4.pdf).

### Caso 2: al diagrama de la arquitectura le faltaba una pieza clave

- **Fase:** diseño.
- **Qué propuso la IA:** Gemini Notebook dibujó el diagrama C4 de contenedores sin la cola
  de tareas (Redis y Celery).
- **Qué estaba mal:** sin la cola, el diagrama mostraba en realidad la alternativa A (un
  solo servidor que hace todo en orden), no la que se escogió en el ADR-001. Esa versión no
  cumplía el requisito RNF-01 de responder en menos de 3 segundos.
- **Cómo lo detecté:** revisé que el diagrama coincidiera con la decisión del ADR-001 y con
  los requisitos no funcionales.
- **Qué hice:** agregué el contenedor de la cola al diagrama. Está en la sección 16 del
  [documento de las semanas 1 a 4](docs/documento_semanas_1_a_4.pdf).

### Caso 3: el código mostraba un "máximo negativo"

- **Fase:** código.
- **Qué propuso la IA:** en la semana 5, la IA escribió calcular_limite_diario. Cuando los
  gastos fijos eran mayores que los ingresos, la función mostraba el mensaje "La meta
  supera tu disponibilidad mensual ($-200.000 COP máximo)".
- **Qué estaba mal:** un máximo negativo no tiene sentido para el usuario. El problema real
  era que los gastos fijos ya superaban los ingresos, y el mensaje no lo decía.
- **Cómo lo detecté:** en la revisión de la semana 6. Ni el linter ni la revisión hecha con
  IA lo encontraron; salió al revisar el código con la lista de revisión.
- **Qué hice:** se agregó un error propio, GastosSuperanIngresosError, con un mensaje
  claro, y una prueba nueva para ese caso. Commit:
  [6789feb](https://github.com/nicolasgutierrezco-beep/smartfinance-ai/commit/6789feb).
  El detalle está en el hallazgo H-02 de [revision_seguridad.md](revision_seguridad.md).

### Caso 4: una prueba esperaba un número que no salía de la regla

- **Fase:** pruebas.
- **Qué propuso la IA:** en el borrador de pruebas, la IA escribió una prueba que esperaba
  que la app recomendara reducir $30.000 en ocio, con un gasto de $120.000 y un tope de
  $100.000.
- **Qué estaba mal:** $120.000 - $100.000 da $20.000. La IA copió el $30.000 del escenario
  de la historia HU-02 sin hacer la cuenta.
- **Cómo lo detecté:** la prueba falló. Antes de tocarla se revisó la regla, y la cuenta
  no daba $30.000.
- **Qué hice:** la prueba quedó esperando $20.000, y la diferencia con la historia quedó
  anotada como la duda A-04 borrador de la IA:
  [2e56a35](https://github.com/nicolasgutierrezco-beep/smartfinance-ai/commit/2e56a35).
    Commit donde quedó la versión corregida: [21c7407](https://github.com/nicolasgutierrezco-beep/smartfinance-ai/commit/21c7407).
  Hoy está en la prueba test_tabla_de_decision[120000-20000].

  ## 5. Estado final del sistema

- **Arquitectura:** el diseño escogido en el ADR-001 es un backend en FastAPI con una cola
  de tareas (Redis y Celery) para que la app responda rápido, la API de un LLM para
  entender las frases de los gastos y PostgreSQL con cifrado para guardar los datos. Está
  en las secciones 16 y 17 del [documento de las semanas 1 a 4](docs/documento_semanas_1_a_4.pdf).
  Lo que está programado hasta ahora es la lógica de negocio, en Python, sin esas piezas
  externas: tres funciones en [src/smartfinance](src/smartfinance).

- **Funcionalidades terminadas:** de las cuatro historias Must:

| Historia | Estado | Qué hay en el código |
|---|---|---|
| HU-01. Registrar gastos en lenguaje natural | No empezada | Necesita la API del LLM |
| HU-02. Recomendaciones de ahorro | Parcial | evaluar_gasto_ocio calcula cuánto recortar si el ocio pasa el tope. Falta que el LLM redacte la recomendación |
| HU-03. Alertas de vencimiento de deudas | Parcial | validar_fecha_vencimiento rechaza fechas de hoy o anteriores. Falta enviar las alertas |
| HU-04. Límite de gasto diario | Terminada en la lógica | calcular_limite_diario hace el cálculo completo con sus validaciones. Falta guardarlo y mostrarlo en una pantalla |

- **Pruebas:** 35 pruebas con pytest, todas en verde: 15 de las semanas 5 y 6 y 20 de la
  versión simplificada. Cubren la lógica de negocio de las tres funciones: los casos
  normales, los valores límite (por ejemplo, hoy y mañana en las fechas, o 4 y 5
  transacciones en el ocio) y los errores. La tabla de casos de cada función está en
  [registro_pruebas.md](registro_pruebas.md). No medí la cobertura con un porcentaje.
  El pipeline de GitHub Actions corre ruff y las pruebas en cada push:
  [última ejecución](https://github.com/nicolasgutierrezco-beep/smartfinance-ai/actions/runs/45973174055).

- **Pendientes:**
  - La API con FastAPI, la cola, la base de datos y la conexión con el LLM. No alcanzaron
    porque el seminario se centró en la lógica, las pruebas y la revisión del código.
  - Las alertas de vencimiento y marcar deudas como pagadas (HU-06). Estuvieron programadas
    en la semana 7, pero las quité al simplificar porque no las pedía la rúbrica y no
    podía explicarlas bien.
  - Confirmar con el profesor las dudas A-01 (si una deuda que vence hoy es válida) y
    A-04 (los $30.000 frente a $20.000).

## 6. Reflexión ética y legal

| Principio | Decisión en mi proyecto | Evidencia |
|---|---|---|
| Datos personales (Ley 1581 de 2012) | En las pruebas solo usé datos inventados, sin nombres, cédulas, correos ni teléfonos de personas reales. El cliente de la entrevista dio permiso para grabarla y procesarla con IA. En el diseño, los datos se guardan cifrados (AES-256) y las claves no se suben al repositorio | [conftest.py](tests/conftest.py), sección 4 de [registro_pruebas.md](registro_pruebas.md), [.env.example](.env.example) y la sección 7.3 del [documento de las semanas 1 a 4](docs/documento_semanas_1_a_4.pdf) |
| Sesgo | La app va a recibir frases en español colombiano, con palabras como "lucas" o "súper", que un LLM podría entender mal. Por eso los datos de prueba tienen contexto local (gastos de Neiva) y casos con tildes, ñ y apóstrofos. Como el LLM todavía no está conectado, probar sus sesgos queda pendiente | Sección 4 de [registro_pruebas.md](registro_pruebas.md) y sección 2.2 del [documento de las semanas 1 a 4](docs/documento_semanas_1_a_4.pdf) |
| Transparencia | La app debe avisarle al usuario cuándo una recomendación la redactó una IA, y que es una sugerencia, no una orden. En el desarrollo, declaré cada uso de IA en la bitácora con su prompt y su verificación, y agregué una nota de corrección cuando unas entradas no dejaban claro quién hizo qué | [bitacora_ia.md](bitacora_ia.md), entradas 1 a 19 y la nota de corrección; sección "Uso de IA" del [README](README.md) |
| Responsabilidad | Los cálculos de plata (el límite diario, cuánto recortar, las fechas) los hace código probado, no el LLM; el LLM solo entiende las frases y redacta los consejos. Si un cálculo sale mal, respondo yo como desarrollador. Por eso simplifiqué el código hasta poder explicarlo, rompí el código a mano para comprobar las pruebas, y el pipeline revisa cada cambio | [src/smartfinance](src/smartfinance), sección 3 de [registro_pruebas.md](registro_pruebas.md) y [pruebas.yml](.github/workflows/pruebas.yml) |
| Propiedad intelectual y política de uso | Usé IA como lo permite el seminario: declarando en cada entrega qué herramienta usé y para qué. No copié código de otros proyectos. Las dos herramientas que usa el proyecto, pytest y ruff, son de código abierto. El README declara la licencia MIT para mi código | Sección "Uso de IA" y sección 8 del [README](README.md), [requirements.txt](requirements.txt) |

El dilema más importante llegó al final del proyecto. Un análisis de mi repositorio
estimó que entre el 85 y el 90 % del contenido parecía escrito por IA, y encontré un
documento con recomendaciones para bajar esa apariencia: cambiar los símbolos que suele
usar la IA, cambiar el estilo del texto y borrar partes del registro que delataban que lo
había hecho un agente. al momento de leer quise pedirle a la ia que modificara todo pero
al final decidi hacerlo a conciencia propia. Tenía dos opciones: disimular el uso de
IA, o hacer más trabajo yo mismo y contar con honestidad quién hizo cada cosa. Escogí el
segundo. Simplifiqué el código hasta poder explicarlo, lo escribí a mano, rompí el código
yo mismo para comprobar las pruebas y agregué una nota en la bitácora aclarando qué
entradas había redactado la IA. Lo decidí porque el seminario permite usar IA siempre que
se declare, y disimularlo habría convertido una herramienta permitida en un engaño.

## 7. Aprendizajes

**Qué sé hacer ahora.** Al empezar nunca había usado Git. Ahora sé crear ramas, hacer
commits con mensajes claros, unir una rama a main, subir cambios a GitHub y deshacer un
cambio con git restore. También aprendí a preparar un entorno de Python, a correr pruebas
con pytest y a leer cuando una falla. Entendí qué son las particiones de equivalencia, los
valores límite y las tablas de decisión, y para qué sirve romper el código a propósito: en
el error 4 aprendí qué es un mutante equivalente. Y armé un pipeline que revisa el código
cada vez que subo cambios. Me costo mucho el poder entender algunas clases ya que sentia que
veia cosas que estaban algo avanzadas para mi.

**En qué confié de más en la IA.** Acepté código que crecía mucho sin entenderlo: la
versión de la semana 7 llegó a unas 1.000 líneas que no podía explicar. También dejé que
la IA redactara entradas de la bitácora en primera persona sin revisar que cada frase
fuera cierta, y por eso tuve que agregar una nota de corrección. En las fases de
requisitos y diseño, la IA inventó un módulo de criptomonedas, se equivocó en el
porcentaje de historias Must y omitió la cola en un diagrama; lo encontré revisando,
pero muestra que no se le puede creer del todo a la IA.

**Qué haría distinto.** Pediría a la IA que me explicara cada parte del código antes de
aceptarlo, y lo mantendría simple desde el principio. Leería todo lo que la IA escribe a
mi nombre antes de guardarlo. Haría yo los commits a medida que trabajo, para que el
historial muestre mi proceso real. Y preguntaría las dudas de las reglas, como la de los
$30.000, al profesor apenas aparecen.

## 8. Anexos

- Bitácora de uso de IA: [bitacora_ia.md](bitacora_ia.md)
- Documentos de cada módulo:
  - Módulos 1 a 3 (fundamentos, requisitos y diseño): [documento de las semanas 1 a 4](docs/documento_semanas_1_a_4.pdf)
  - Módulo 4 (código y revisión): [presupuesto.py](src/smartfinance/presupuesto.py), [revision_seguridad.md](revision_seguridad.md) y [README](README.md)
  - Módulo 5 (pruebas): [registro_pruebas.md](registro_pruebas.md) y la carpeta [tests](tests)
    - Módulo 6 (operación): [pruebas.yml](.github/workflows/pruebas.yml), [guía de despliegue](docs/guia_despliegue.md) y [plan de operación](docs/plan_operacion.md)