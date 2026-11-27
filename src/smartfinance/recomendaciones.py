"""recomendaicones de ahooro por gasto en ocio (HU-02)."""

MINIMO_TRANSACCIONES = 5

def evaluar_gasto_ocio(transacciones, tope_ocio):
    """Dice cuanto debe recortar el usuario en ocio este mes.
    
    Recibe una lista de transacciones (diccionarios con "monto" y "categoria")
    y el tope mensual de ocio. Devuelve cuanto se paso del tope, o 0 si no se
    paso. Lanza ValueError si hay menos de 5 transacciones."""

    if len(transacciones) < MINIMO_TRANSACCIONES:
        raise ValueError(
            "Se requieren al menos 5 transacciones registradas "
            "para generar sugerencias personalizadas"
        )
    gasto_ocio = 0
    for transaccion in transacciones:
        if transaccion["categoria"] == "Ocio":
            gasto_ocio += transaccion["monto"]
    if gasto_ocio > tope_ocio:
        return gasto_ocio - tope_ocio
    return 0