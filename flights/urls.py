from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='homepage'),
    path('details/<int:flight_id>', views.FlightDetails.as_view(), name='flight_details')
]
