# Sensors API

Django REST API для управления событиями датчиков с поддержкой загрузки данных из JSON файлов.

## Функциональность

- **CRUD операции** для датчиков и событий
- **Загрузка событий** из JSON файлов
- **Фильтрация и пагинация** событий
- **Валидация данных** через DRF сериализаторы
- **Автодокументация API** через Swagger
- **Тестовое покрытие** 28+ тестов
- **Docker контейнеризация**

## Технологии

- **Backend**: Django 5.2 + Django REST Framework
- **Database**: PostgreSQL 14
- **ASGI Server**: Uvicorn
- **Testing**: Pytest + Django Test Framework
- **Linting**: Ruff, Black, Mypy
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

## Быстрый старт

### Локальная разработка

1. **Клонируйте репозиторий**:
```bash
git clone https://github.com/yourusername/sensors-api.git
cd sensors-api
```

2. **Настройте окружение**:
```bash
cp .env.example .env
```
# Отредактируйте .env при необходимости

3. **Запустите через Docker**:
```bash
docker-compose up --build
```

4. **API будет доступно по адресу**: 
http://localhost:8080


## API Endpoints
**Датчики**:
- **GET /api/sensors/** - список датчиков
- **POST /api/sensors/** - создать датчик
- **GET /api/sensors/{id}/** - получить датчик
- **PUT /api/sensors/{id}/** - обновить датчик
- **DELETE /api/sensors/{id}/** - удалить датчик
- **GET /api/sensors/{id}/events/** - события датчика

**События**:
- **GET /api/events/** - список событий
- **POST /api/events/** - создать событие
- **GET /api/events/{id}/** - получить событие
- **PUT /api/events/{id}/** - обновить событие
- **DELETE /api/events/{id}/** - удалить событие

**Документация**:

- **GET /swagger/** - Swagger документация
- **GET /redoc/** - ReDoc документация


## Фильтрация событий
**Доступные параметры фильтрации для /api/events/:**

- **sensor_id** - фильтр по ID датчика
- **temperature_min** - минимальная температура
- **temperature_max** - максимальная температура
- **humidity_min** - минимальная влажность
- **humidity_max** - максимальная влажность

**Пример**:
```bash
GET /api/events/?temperature_min=20&temperature_max=30&sensor_id=1
```

**Запуск тестов:**
```bash
# Все тесты
docker-compose exec api pytest

# С покрытием кода
docker-compose exec api pytest --cov=.

# Конкретный тест
docker-compose exec api pytest sensors/app/tests/test_models.py -v
```

**Проверка качества кода**:
```bash
# Форматирование
docker-compose exec api ruff format .

# Линтинг
docker-compose exec api ruff check .

# Проверка типов
docker-compose exec api mypy .
```

## Модели данных

**Sensor (Датчик)**:

```python
{
    "id": 1,
    "name": "Датчик температуры",
    "sensor_type": 1,  # 1, 2 или 3
    "created_at": "2024-01-01T12:00:00Z"
}
```

**Event (Событие)**:
```python

{
    "id": 1,
    "sensor": 1,
    "name": "Высокая температура",
    "temperature": 25.5,  # -200 до 200°C
    "humidity": 60.0,     # 0 до 100%
    "created_at": "2024-01-01T12:00:00Z"
}
```


## Загрузка JSON файлов

**Формат JSON для загрузки:**
```json
[
    {
        "sensor_id": 1,
        "name": "Событие 1",
        "temperature": 25.5,
        "humidity": 60.0
    },
    {
        "sensor_id": 2,
        "name": "Событие 2", 
        "temperature": 20.0
    }
]
```

**Пример загрузки через curl:**
```bash
curl -X POST \
  http://localhost:8080/api/load-events/ \
  -F "json_file=@events.json"
```

## Docker команды

# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Просмотр логов
docker-compose logs -f api

# Выполнение команд в контейнере
docker-compose exec api python manage.py migrate
docker-compose exec api bash


## Переменные окружения

```bash
POSTGRES_DB=sensors_db
POSTGRES_USER=sensors_user
POSTGRES_PASSWORD=user
DJANGO_DATABASE_HOST=db
DJANGO_DATABASE_PORT=5432
DJANGO_SECRET_KEY=your-secret-key
```