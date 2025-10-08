import pytest
from sensors.app.models import Sensor, Event


@pytest.mark.django_db
class TestSensorModel:
    def test_create_sensor(self):
        sensor = Sensor.objects.create(name='Test Sensor', sensor_type=Sensor.SensorType.TYPE_1)
        assert sensor.name == 'Test Sensor'
        assert sensor.sensor_type == 1

    def test_sensor_type_choices(self):
        sensor = Sensor.objects.create(name='Test Sensor', sensor_type=Sensor.SensorType.TYPE_3)
        assert sensor.sensor_type == 3

    def test_sensor_created_at_auto_now(self):
        sensor = Sensor.objects.create(name='Test Sensor', sensor_type=Sensor.SensorType.TYPE_1)
        assert sensor.created_at is not None


@pytest.mark.django_db
class TestEventModel:
    def test_create_event(self):
        sensor = Sensor.objects.create(name='Test Sensor', sensor_type=Sensor.SensorType.TYPE_1)
        event = Event.objects.create(sensor=sensor, name='Test Event', temperature=25.5, humidity=60.0)
        assert event.temperature == 25.5
        assert event.humidity == 60.0
        assert event.sensor == sensor

    def test_event_temperature_constraint(self):
        sensor = Sensor.objects.create(name='Test Sensor', sensor_type=Sensor.SensorType.TYPE_1)
        event = Event.objects.create(sensor=sensor, name='Valid Temp', temperature=200)
        assert event.temperature == 200

    def test_event_humidity_constraint(self):
        sensor = Sensor.objects.create(name='Test Sensor', sensor_type=Sensor.SensorType.TYPE_1)
        event = Event.objects.create(sensor=sensor, name='Valid Humidity', humidity=100)
        assert event.humidity == 100

    def test_event_created_at_auto_now(self):
        sensor = Sensor.objects.create(name='Test Sensor', sensor_type=Sensor.SensorType.TYPE_1)
        event = Event.objects.create(sensor=sensor, name='Test Event')
        assert event.created_at is not None

    def test_event_optional_fields(self):
        sensor = Sensor.objects.create(name='Test Sensor', sensor_type=Sensor.SensorType.TYPE_1)
        event = Event.objects.create(sensor=sensor, name='Minimal Event')
        assert event.temperature is None
        assert event.humidity is None
