import pytest
from sensors.app.serializers import SensorSerializer, EventSerializer


@pytest.mark.django_db
class TestSensorSerializer:
    def test_valid_serializer(self):
        data = {
            "name": "Test Sensor",
            "sensor_type": 1
        }
        serializer = SensorSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["name"] == "Test Sensor"

    def test_invalid_sensor_type(self):
        data = {
            "name": "Test Sensor",
            "sensor_type": 999
        }
        serializer = SensorSerializer(data=data)
        assert not serializer.is_valid()
        assert "sensor_type" in serializer.errors


@pytest.mark.django_db
class TestEventSerializer:
    def test_valid_serializer(self):
        from sensors.app.models import Sensor
        sensor = Sensor.objects.create(
            name="Test Sensor",
            sensor_type=Sensor.SensorType.TYPE_1
        )
        data = {
            "sensor": sensor.id,
            "name": "Test Event",
            "temperature": 25.5,
            "humidity": 60.0
        }
        serializer = EventSerializer(data=data)
        assert serializer.is_valid()

    def test_event_without_sensor(self):
        data = {
            "name": "Test Event",
            "temperature": 25.5
        }
        serializer = EventSerializer(data=data)
        assert not serializer.is_valid()
        assert "sensor" in serializer.errors

    def test_event_temperature_validation(self):
        from sensors.app.models import Sensor
        sensor = Sensor.objects.create(
            name="Test Sensor",
            sensor_type=Sensor.SensorType.TYPE_1
        )
        data = {
            "sensor": sensor.id,
            "name": "Test Event", 
            "temperature": "invalid"
        }
        serializer = EventSerializer(data=data)
        assert not serializer.is_valid()
        assert "temperature" in serializer.errors
