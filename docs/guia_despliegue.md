# Guía de despliegue

## Estado actual

SmartFinance AI todavía no está desplegado en un servidor. Lo que existe es la lógica de
negocio en Python con sus pruebas. Esta guía explica cómo instalarlo y verificarlo en un
computador, y qué falta para el despliegue completo.

## Requisitos

- Python 3.11 o mayor
- Git

## Instalación

1. Clonar el repositorio:
   `git clone https://github.com/nicolasgutierrezco-beep/smartfinance-ai.git`
2. Entrar a la carpeta: `cd smartfinance-ai`
3. Crear el entorno: `python -m venv .venv`
4. Activarlo en Windows: `.venv\Scripts\activate`
5. Instalar las dependencias: `pip install -r requirements.txt`

## Verificación

- Pruebas: `pytest -v`. Deben pasar las 35.
- Linter: `pip install ruff` y luego `ruff check .`. Debe decir "All checks passed!".

## Despliegue previsto (pendiente)

Según el ADR-001 del documento de diseño, el despliegue completo necesita un backend en
FastAPI, Redis y Celery para la cola de tareas, PostgreSQL con cifrado y una clave de la
API del LLM. Las claves van en un archivo .env, que nunca se sube al repositorio; los
nombres de las variables están en .env.example.