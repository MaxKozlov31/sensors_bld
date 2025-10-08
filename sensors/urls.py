from django.conf.urls import include
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from sensors.app.views import EventViewSet
from sensors.app.views import LoadEventsAPIView
from sensors.app.views import SensorViewSet


schema_view = get_schema_view(
    openapi.Info(
        title='Sensors',
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'sensors', SensorViewSet, basename='sensors')
router.register(r'events', EventViewSet, basename='events')


urlpatterns = [
    path('', include(router.urls)),
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui',
    ),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path(
        'load-events/',
        LoadEventsAPIView.as_view(),
        name='load-events',
    ),
]
