import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestSensorViewSet:
    def test_list_sensors(self, api_client, sensor, sensor_2):
        url = reverse('sensors-list')
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data['count'] == 2

    def test_retrieve_sensor(self, api_client, sensor):
        url = reverse('sensors-detail', kwargs={'pk': sensor.id})
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data['name'] == sensor.name

    def test_create_sensor(self, api_client):
        url = reverse('sensors-list')
        data = {
            "name": "New Sensor",
            "sensor_type": 2
        }
        response = api_client.post(url, data)
        assert response.status_code == 201
        assert response.data['name'] == "New Sensor"

    def test_update_sensor(self, api_client, sensor):
        url = reverse('sensors-detail', kwargs={'pk': sensor.id})
        data = {
            "name": "Updated Sensor",
            "sensor_type": 3
        }
        response = api_client.put(url, data)
        assert response.status_code == 200
        assert response.data['name'] == "Updated Sensor"

    def test_delete_sensor(self, api_client, sensor):
        url = reverse('sensors-detail', kwargs={'pk': sensor.id})
        response = api_client.delete(url)
        assert response.status_code == 204

    def test_sensor_events_endpoint(self, api_client, sensor, event):
        url = reverse('sensors-events', kwargs={'pk': sensor.id})
        response = api_client.get(url)
        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == event.name


@pytest.mark.django_db
class TestEventViewSet:
    def test_list_events(self, api_client, event, event_2):
        url = reverse('events-list')
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data['count'] == 2

    def test_filter_events_by_temperature(self, api_client, event, event_2):
        url = reverse('events-list')
        response = api_client.get(url, {'temperature_min': 22})
        assert response.status_code == 200
        assert response.data['count'] == 1

    def test_filter_events_by_humidity(self, api_client, event, event_2):
        url = reverse('events-list')
        response = api_client.get(url, {'humidity_max': 50})
        assert response.status_code == 200
        assert response.data['count'] == 1

    def test_filter_events_by_sensor(self, api_client, sensor, event):
        url = reverse('events-list')
        response = api_client.get(url, {'sensor_id': sensor.id})
        assert response.status_code == 200
        assert response.data['count'] == 1

    def test_create_event(self, api_client, sensor):
        url = reverse('events-list')
        data = {
            "sensor": sensor.id,
            "name": "New Event",
            "temperature": 22.5,
            "humidity": 55.0
        }
        response = api_client.post(url, data)
        assert response.status_code == 201
        assert response.data['name'] == "New Event"

    def test_create_event_with_invalid_sensor(self, api_client):
        url = reverse('events-list')
        data = {
            "sensor": 999,
            "name": "New Event",
            "temperature": 22.5
        }
        response = api_client.post(url, data)
        assert response.status_code == 400


@pytest.mark.django_db
class TestLoadEventsAPIView:
    def test_load_valid_events(self, api_client, sensor, sensor_2, valid_events_json):
        sensor.id = 1
        sensor.save()
        sensor_2.id = 2
        sensor_2.save()

        url = reverse('load-events')
        response = api_client.post(
            url,
            {'json_file': valid_events_json},
            format='multipart'
        )
        assert response.status_code == 201
        assert response.data['created'] == 2

    def test_load_invalid_json(self, api_client, invalid_events_json):
        url = reverse('load-events')
        response = api_client.post(
            url,
            {'json_file': invalid_events_json},
            format='multipart'
        )
        assert response.status_code == 400

    def test_load_events_missing_sensors(self, api_client, valid_events_json):
        url = reverse('load-events')
        response = api_client.post(
            url,
            {'json_file': valid_events_json},
            format='multipart'
        )
        assert response.status_code == 400
        assert "skipped_events_to_missing_sensor" in response.data
        assert response.data["skipped_events_to_missing_sensor"] == 2
