from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework_jwt.views import obtain_jwt_token

from api.views import FlightViewSet, CrewView, WorkersViewSet

router = SimpleRouter()
router.register('flights', FlightViewSet)
router.register('workers', WorkersViewSet)

urlpatterns = [
    path('obtain-token/', obtain_jwt_token),
    path('', include(router.urls)),
    path('flights/<int:flight_id>/crew/<int:worker_id>/', CrewView.as_view(), name='crew')
]
