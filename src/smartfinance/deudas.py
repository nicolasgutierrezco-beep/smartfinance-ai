"""Deudas (HU-03): validar la fecha de vencimiento de una deuda nueva."""


def validar_fecha_vencimiento(fecha_vencimiento, hoy):
    """Revisa que una deuda nueva venza después de hoy.

    Recibe dos fechas (date). Si todo está bien no devuelve nada.
    Lanza ValueError si la fecha de vencimiento es hoy o ya pasó.
    """
    if fecha_vencimiento <= hoy:
        raise ValueError("La fecha de vencimiento debe ser posterior a la fecha actual")