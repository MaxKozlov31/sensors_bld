from django.db import models
from django.db.models import Q


class Sensor(models.Model):
    class SensorType:
        TYPE_1 = 1
        TYPE_2 = 2
        TYPE_3 = 3
        TYPES = ((TYPE_1, 'Тип 1'), (TYPE_2, 'Тип 2'), (TYPE_3, 'Тип 3'))

    name = models.CharField(max_length=500, null=True, blank=True)
    sensor_type = models.SmallIntegerField(choices=SensorType.TYPES)
    created_at = models.DateTimeField(auto_now_add=True)


class Event(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='events')
    name = models.CharField(max_length=255, null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['sensor', '-created_at']),
            models.Index(fields=['temperature']),
            models.Index(fields=['humidity']),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(temperature__gte=-200) & Q(temperature__lte=200),
                name='temperature_range',
            ),
            models.CheckConstraint(check=Q(humidity__gte=0) & Q(humidity__lte=100), name='humidity_range'),
        ]
