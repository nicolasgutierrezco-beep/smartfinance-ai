# Informe final del proyecto integrador

Proyecto: SmartFinance AI
Estudiante: Nicolás Andrés Gutiérrez Collazos
Repositorio: https://github.com/nicolasgutierrezco-beep/smartfinance-ai
Fecha: 2026-11-27

## 1. Resumen

(esta al final.)

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
| 6. Operación | Agregué un pipeline que corre ruff y pytest cada vez que subo cambios | Claude | [pruebas.yml](.github/workflows/pruebas.yml) y la pestaña Actions del repositorio | La primera ejecución del pipeline pasó en verde |