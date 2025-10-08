import pytest
import django
from django.conf import settings
import os

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sensors.settings')
    django.setup()

from sensors.app.models import Sensor, Event
from django.core.files.uploadedfile import SimpleUploadedFile
import json


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    client = APIClient()
    client.default_format = 'json'
    return client


@pytest.fixture
def sensor():
    return Sensor.objects.create(name='Test Sensor', sensor_type=Sensor.SensorType.TYPE_1)


@pytest.fixture
def sensor_2():
    return Sensor.objects.create(name='Test Sensor 2', sensor_type=Sensor.SensorType.TYPE_2)


@pytest.fixture
def event(sensor):
    return Event.objects.create(sensor=sensor, name='Temperature High', temperature=25.5, humidity=60.0)


@pytest.fixture
def event_2(sensor_2):
    return Event.objects.create(sensor=sensor_2, name='Humidity Low', temperature=20.0, humidity=30.0)


@pytest.fixture
def valid_events_json():
    """Валидный JSON файл для тестирования загрузки"""
    data = [
        {'sensor_id': 1, 'name': 'Event 1', 'temperature': 25.5, 'humidity': 60.0},
        {'sensor_id': 2, 'name': 'Event 2', 'temperature': 20.0, 'humidity': 45.5},
    ]
    return SimpleUploadedFile('events.json', json.dumps(data).encode('utf-8'), content_type='application/json')


@pytest.fixture
def invalid_events_json():
    """Невалидный JSON файл"""
    return SimpleUploadedFile('events.json', b'invalid json content', content_type='application/json')
