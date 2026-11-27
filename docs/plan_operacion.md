# Plan de operación

## Lo que funciona hoy

- **Pipeline de GitHub Actions** (.github/workflows/pruebas.yml): cada vez que se suben
  cambios, corre ruff y las 35 pruebas. El resultado se ve en la pestaña Actions del
  repositorio.
- **Regla de trabajo:** cada cambio se hace en una rama aparte. Si el pipeline falla, la
  rama no se une a main hasta que vuelva a estar en verde.
- **Dependencias:** pytest y ruff tienen la versión fija para que el resultado sea
  siempre el mismo.

## Qué hacer si el pipeline falla

1. Abrir la ejecución en Actions y ver qué paso falló: el linter o las pruebas.
2. Si falla una prueba, revisar primero la regla de la historia de usuario. Si la regla
   dice que la prueba está bien, se corrige el código; nunca se cambia la prueba para que
   pase.
3. Corregir en la rama, subir y comprobar que vuelva a verde.

## Pendiente para cuando la app esté desplegada

- Medir que la app responda en menos de 3 segundos (requisito RNF-01).
- Registrar los errores de la API del LLM, por ejemplo cuando no entiende una frase.
- Revisar cada cierto tiempo que las dependencias no tengan vulnerabilidades conocidas,
  con pip-audit.
- Responsable de la operación: el desarrollador del proyecto.