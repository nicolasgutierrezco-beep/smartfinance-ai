# Registro de pruebas: tabla de casos y pruebas de la IA

Proyecto: SmartFinance AI
Estudiante: Nicolás Andrés Gutiérrez Collazos
Fecha: 2026-11-22

## 1. Tabla de casos

(En construcción: reglas y ambigüedades escritas antes de generar las pruebas.)

### Reglas que se van a probar

| Función | Historia | Regla (el oráculo) |
|---|---|---|
| `calcular_limite_diario` | HU-04 | (ingresos − gastos fijos − meta − gastado) ÷ días que faltan contando hoy, en pesos enteros hacia abajo, nunca negativo. |
| `validar_fecha_vencimiento` | HU-03 esc. 2 | «La fecha de vencimiento debe ser posterior a la fecha actual». |
| `generar_alerta_vencimiento` | HU-03 esc. 1 | Deuda pendiente que vence en 2 días → «Recordatorio: tu tarjeta de crédito por $200.000 COP vence en 2 días». |
| `marcar_como_pagada` y `total_pendiente` | HU-06 | Pendiente pasa a Pagado y su monto sale del total; pagar dos veces → «Esta deuda ya ha sido saldada previamente». |
| `evaluar_gasto_ocio` | HU-02 | Menos de 5 transacciones → error; ocio por encima del tope → recomendación de reducir. |

### Ambigüedades detectadas al escribir las reglas

- A-01: ¿Una deuda que vence hoy es «posterior a la fecha actual»?
- A-02: ¿La alerta sale solo a los 2 días exactos, o también a 1 día y el mismo día?
- A-03: ¿Una deuda ya vencida y sin pagar genera alerta preventiva?
- A-04: El escenario 1 de HU-02 pide reducir $30.000 con un exceso de $20.000. ¿De dónde sale $30.000?
- A-05: ¿Gastar exactamente el tope de ocio es «superarlo»?
- A-06: ¿Cuentan para el mínimo de 5 las transacciones de cualquier categoría?
