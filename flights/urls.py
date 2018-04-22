from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='homepage'),
    path('details/<int:flight_id>', views.flight_details, name='flight_details'),
    path('add_passenger/<int:flight_id>', views.add_passenger, name='add_passenger')
]
