from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_jwt.views import ObtainJSONWebToken, obtain_jwt_token

from api.views import FlightViewSet, CrewView, WorkersViewSet

router = DefaultRouter()
router.register('flights', FlightViewSet)
router.register('workers', WorkersViewSet)

urlpatterns = [
    path('obtain-token', obtain_jwt_token),
    path('', include(router.urls)),
    path('flights/<int:flight_id>/crew/<int:worker_id>', CrewView.as_view(), name='crew')
]