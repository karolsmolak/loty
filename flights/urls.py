from django.urls import path

from . import views

urlpatterns = [
    path('', views.FlightList.as_view(), name='homepage'),
    path('details/<int:pk>', views.FlightDetails.as_view(), name='flight_details')
]
