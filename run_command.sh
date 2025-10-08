#!/usr/bin/env sh

echo "Running code quality checks..."
ruff format . && echo "✓ Formatting done"
ruff check . && echo "✓ Linting done"
mypy . && echo "✓ Type checking done"

python manage.py migrate

uvicorn sensors.asgi:application --host 0.0.0.0 --port 8080 --reload
