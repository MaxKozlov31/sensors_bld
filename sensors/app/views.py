import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from sensors.app.exceptions import ParseError
from sensors.app.filters import EventFilter
from sensors.app.models import Event
from sensors.app.models import Sensor
from sensors.app.serializers import EventSerializer
from sensors.app.serializers import LoadEventsSerializer
from sensors.app.serializers import SensorSerializer
from sensors.app.services import EventDataParser
from sensors.app.services import EventService


logger = logging.getLogger(__name__)


class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all().order_by('id')
    serializer_class = SensorSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'created_at']

    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        sensor = self.get_object()
        events = sensor.events.all().order_by('-created_at')
        page = self.paginate_queryset(events)
        serializer = EventSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-created_at')
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = EventFilter
    # filterset_fields = ['temperature', 'humidity', 'sensor']
    ordering_fields = ['created_at', 'temperature', 'humidity', 'id']


class LoadEventsAPIView(APIView):
    parser_classes = (MultiPartParser,)
    serializer_class = LoadEventsSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        upload = serializer.validated_data['json_file']
        # default_type = serializer.validated_data.get("default_sensor_type", 1)

        try:
            valid_events, parse_errors = EventDataParser.parse_json_file(upload.file)
            # if errors:
            #     return Response(
            #         {"detail": "Ошибки валидации", "errors": errors},
            #         status=status.HTTP_400_BAD_REQUEST,
            #     )

            sensor_ids = {event['sensor_id'] for event in valid_events}
            # sensors_map = SensorService.get_or_create_sensors(sensor_ids)
            existing_sensors = Sensor.objects.filter(id__in=sensor_ids)
            existing_sensors_map = {sensor.id: sensor for sensor in existing_sensors}

            created_count, sensor_errors = EventService.bulk_create_events(valid_events, existing_sensors_map)

            all_errors = parse_errors + sensor_errors

            status_code = status.HTTP_201_CREATED if created_count > 0 else status.HTTP_400_BAD_REQUEST

            return Response(
                {
                    'total_input': len(valid_events) + len(parse_errors),
                    'valid_events': len(valid_events),
                    'created': created_count,
                    'skipped_events_to_missing_sensor': len(sensor_errors),
                    'parse_errors': len(parse_errors),
                    'error_details': all_errors,
                },
                status=status_code,
            )

        except ParseError as e:
            return Response({'detail': str(e)}, status=400)
        except Exception as e:
            logger.error(f'Ошибка загрузки: {e!s}')
            return Response({'detail': 'Внутренняя ошибка'}, status=500)
