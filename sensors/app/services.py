import json

from io import TextIOWrapper

from django.db import transaction

from sensors.app.exceptions import ParseError
from sensors.app.models import Event
from sensors.app.models import Sensor


class EventDataParser:
    @staticmethod
    def parse_json_file(file):
        try:
            data = json.load(TextIOWrapper(file, encoding='utf-8'))
        except json.JSONDecodeError as e:
            raise ParseError(f'Невалидный JSON: {e}') from e

        if not isinstance(data, list):
            raise ParseError('JSON должен быть массивом')

        return EventDataValidator.validate_events(data)


class EventDataValidator:
    @staticmethod
    def validate_events(raw_events):
        if not isinstance(raw_events, list):
            return [], ['JSON должен быть массивом событий']

        result = []
        errors = []
        for idx, item in enumerate(raw_events, start=1):
            if not isinstance(item, dict):
                errors.append(f'#{idx}: элемент не объект')
                continue
            sensor_id = item.get('sensor_id')
            name = item.get('name')
            temperature = item.get('temperature')
            humidity = item.get('humidity')

            if not sensor_id:
                errors.append(f'#{idx}: отсутствует поле sensor_id')
                continue

            if not temperature and not humidity:
                errors.append(f'#{idx}: событие без параметров (отсутствуют temperature и humidity)')
                continue

            try:
                sensor_id = int(sensor_id)
            except Exception:
                errors.append(f'#{idx}: sensor_id не целое число')
                continue
            if sensor_id <= 0:
                errors.append(f'#{idx}: sensor_id должен быть > 0')
                continue

            name_str = str(name).strip()
            if not name_str:
                errors.append(f'#{idx}: name пустой')
                continue

            if temperature:
                try:
                    temperature = float(temperature)
                except Exception:
                    errors.append(f'#{idx}: temperature не число')
                    continue

                if not (-100.0 <= temperature <= 200.0):
                    errors.append(f'#{idx}: temperature вне диапазона [-100; 200]')
                    continue

            if humidity:
                try:
                    humidity = float(humidity)
                except Exception:
                    errors.append(f'#{idx}: humidity не число')
                    continue

                if not (0.0 <= humidity <= 100.0):
                    errors.append(f'#{idx}: humidity вне диапазона [0; 100]')
                    continue

            result.append(
                {
                    'sensor_id': sensor_id,
                    'name': name_str,
                    'temperature': temperature,
                    'humidity': humidity,
                }
            )
        return result, errors


class SensorService:
    @staticmethod
    @transaction.atomic
    def get_or_create_sensors(sensor_ids, default_type):
        existing_sensors = Sensor.objects.filter(id__in=sensor_ids)
        existing_map = {sensor.id: sensor for sensor in existing_sensors}
        missing_ids = sensor_ids - set(existing_map.keys())

        if missing_ids:
            sensors_to_create = [
                Sensor(
                    id=sensor_id,
                    name=f'auto_sensor_{sensor_id}',
                    sensor_type=default_type,
                )
                for sensor_id in sorted(missing_ids)
            ]
            created_sensors = Sensor.objects.bulk_create(sensors_to_create)
            for sensor in created_sensors:
                existing_map[sensor.id] = sensor

        return existing_map


class EventService:
    @staticmethod
    @transaction.atomic
    def bulk_create_events(validated_data, sensors_map):
        events_to_create = []
        missing_sensor_errors = []

        for row in validated_data:
            sensor_id = row['sensor_id']
            sensor = sensors_map.get(sensor_id)
            if sensor:
                events_to_create.append(
                    Event(
                        sensor=sensor,
                        name=row['name'],
                        temperature=row['temperature'],
                        humidity=row['humidity'],
                    )
                )
            else:
                missing_sensor_errors.append(f"Датчик ID {sensor_id} не существует. Событие '{row['name']}' пропущено.")

        if events_to_create:
            Event.objects.bulk_create(events_to_create, batch_size=100)

        return len(events_to_create), missing_sensor_errors


def parse_json_events(data):
    if not isinstance(data, list):
        return [], ['JSON должен быть массивом событий']

    result = []
    errors = []
    for idx, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            errors.append(f'#{idx}: элемент не объект')
            continue
        sensor_id = item.get('sensor_id')
        name = item.get('name')
        temperature = item.get('temperature')
        humidity = item.get('humidity')

        if not sensor_id:
            errors.append(f'#{idx}: отсутствует поле sensor_id')
            continue

        if not temperature and not humidity:
            errors.append(f'#{idx}: событие без параметров (отсутствуют temperature и humidity)')
            continue

        # sensor_id
        try:
            sensor_id = int(sensor_id)
        except Exception:
            errors.append(f'#{idx}: sensor_id не целое число')
            continue
        if sensor_id <= 0:
            errors.append(f'#{idx}: sensor_id должен быть > 0')
            continue

        # name
        name_str = str(name).strip()
        if not name_str:
            errors.append(f'#{idx}: name пустой')
            continue

        # temperature / humidity
        if temperature:
            try:
                temperature = float(temperature)
            except Exception:
                errors.append(f'#{idx}: temperature не число')
                continue

            if not (-100.0 <= temperature <= 200.0):
                errors.append(f'#{idx}: temperature вне диапазона [-100; 200]')
                continue
        if humidity:
            try:
                humidity = float(humidity)
            except Exception:
                errors.append(f'#{idx}: humidity не число')
                continue

            if not (0.0 <= humidity <= 100.0):
                errors.append(f'#{idx}: humidity вне диапазона [0; 100]')
                continue

        result.append(
            {
                'sensor_id': sensor_id,
                'name': name_str,
                'temperature': temperature,
                'humidity': humidity,
            }
        )
    return result, errors
