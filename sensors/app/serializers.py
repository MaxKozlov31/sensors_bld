import logging

from rest_framework import serializers

from sensors.app.models import Event
from sensors.app.models import Sensor


logger = logging.getLogger(__name__)


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    def validate_sensor_type(self, value):
        if value not in [1, 2, 3]:
            raise serializers.ValidationError('Тип датчика должен быть 1, 2 или 3')
        return value

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Имя датчика не может быть пустым')
        if len(value) > 500:
            raise serializers.ValidationError('Имя датчика не может превышать 500 символов')
        return value.strip()


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    def validate_sensor_id(self, value):
        if not Sensor.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'Датчик с ID {value} не существует')
        return value

    def validate_temperature(self, value):
        if value is not None:
            if not isinstance(value, (int, float)):
                raise serializers.ValidationError('Температура должна быть числом')
            if not (-200 <= value <= 200):
                raise serializers.ValidationError('Температура должна быть в диапазоне от -200 до 200°C')
        return value

    def validate_humidity(self, value):
        if value is not None:
            if not isinstance(value, (int, float)):
                raise serializers.ValidationError('Влажность должна быть числом')
            if not (0 <= value <= 100):
                raise serializers.ValidationError('Влажность должна быть в диапазоне от 0 до 100%')
        return value

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Имя события не может быть пустым')
        if len(value) > 255:
            raise serializers.ValidationError('Имя события не может превышать 255 символов')
        return value.strip()

    def validate(self, data):
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        if temperature is None and humidity is None:
            raise serializers.ValidationError(
                'Событие должно содержать хотя бы один параметр (температуру или влажность)'
            )

        return data


class LoadEventsSerializer(serializers.Serializer):
    json_file = serializers.FileField(
        validators=[],
        required=True,
        write_only=True,
    )

    def validate(self, attrs):
        f = attrs['json_file']
        name = (f.name or '').lower()
        if not name.endswith('.json'):
            raise serializers.ValidationError({'json_file': 'Ожидается .json файл'})

        if f.size > 5 * 1024 * 1024:
            raise serializers.ValidationError({'json_file': 'Файл слишком большой (макс. 5MB)'})

        return attrs
