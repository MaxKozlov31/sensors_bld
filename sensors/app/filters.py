import django_filters

from sensors.app.models import Event


class EventFilter(django_filters.FilterSet):
    sensor_id = django_filters.NumberFilter(field_name='sensor_id')
    temperature_min = django_filters.NumberFilter(field_name='temperature', lookup_expr='gte')
    temperature_max = django_filters.NumberFilter(field_name='temperature', lookup_expr='lte')
    humidity_min = django_filters.NumberFilter(field_name='humidity', lookup_expr='gte')
    humidity_max = django_filters.NumberFilter(field_name='humidity', lookup_expr='lte')

    class Meta:
        model = Event
        fields = [
            'sensor_id',
            'temperature_min',
            'temperature_max',
            'humidity_min',
            'humidity_max',
        ]
