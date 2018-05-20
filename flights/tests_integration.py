from django.contrib.auth.models import AnonymousUser, User
from django.http import Http404
from django.test import TestCase, RequestFactory
from django.utils import timezone

from crews.models import Crew, Worker
from .models import Flight, Airplane, Ticket
from .views import FlightDetails


class RequestsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        worker = Worker.objects.create(name="a", surname="b")
        crew = Crew.objects.create(captain=worker)
        crew.workers.add(worker)
        self.ticket_data = {
            "name": "passenger_name",
            "surname": "passenger_surname",
            "count": 1
        }
        self.user = User.objects.create_user(
            username='user1',
            email='email@...',
            password='secret'
        )
        Flight.objects.create(start=timezone.now(),
                              landing=timezone.now(),
                              airplane=Airplane.objects.create(registration_number="airplane",
                                                               capacity=20),
                              start_airport="start",
                              landing_airport="landing",
                              crew=crew)

    def test_get_flight_details_unknown_flight_id_should_raise_404(self):
        request = self.factory.get('details/99')
        with self.assertRaises(Http404):
            FlightDetails.as_view()(request, pk=99)

    def test_add_passenger_unknown_flight_id_should_raise_404(self):
        request = self.factory.post('details/99')
        request.user = self.user
        request.POST = self.ticket_data
        with self.assertRaises(Http404):
            FlightDetails.as_view()(request, pk=99)

    def test_add_passenger_unauthorized_shouldnt_book_ticket(self):
        request = self.factory.post('details/1')
        request.user = AnonymousUser()
        request.POST = self.ticket_data
        FlightDetails.as_view()(request, pk=1)
        self.assertFalse(Ticket.objects.filter(flight_id=1, count=self.ticket_data["count"]).exists())

    def test_valid_add_passenger_should_book_ticket(self):
        request = self.factory.post('details/1')
        request.user = self.user
        request.POST = self.ticket_data
        FlightDetails.as_view()(request, pk=1)
        self.assertTrue(Ticket.objects.filter(flight_id=1, count=self.ticket_data["count"]).exists())
