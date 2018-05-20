from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from crews.models import Crew, Worker
from flights.models import Flight, Airplane


def advance_date(date, hours=0, minutes=0, seconds=0):
    return date + timezone.timedelta(hours=hours, minutes=minutes, seconds=seconds)

class ValidationTests(TestCase):
    def create_flight(self, start, landing, airplane, crew):
        return Flight.objects.create(start=start,
                                     landing=landing,
                                     airplane=airplane,
                                     start_airport="start",
                                     landing_airport="finish",
                                     crew=crew).full_clean()

    def setUp(self):
        self.airplane1 = Airplane.objects.create(registration_number="samolocik1", capacity=40)
        self.airplane2 = Airplane.objects.create(registration_number="samolocik2", capacity=40)
        self.worker1 = Worker.objects.create(name="worker1", surname="worker1")
        self.worker2 = Worker.objects.create(name="worker2", surname="worker2")
        self.worker3 = Worker.objects.create(name="worker3", surname="worker3")
        self.crew1 = Crew.objects.create(captain=self.worker1)
        self.crew1.workers.add(self.worker1, self.worker2)
        self.crew2 = Crew.objects.create(captain=self.worker3)
        self.crew2.workers.add(self.worker2, self.worker3)


    def test_worker_simultinously_in_two_flights(self):
        self.create_flight(timezone.now(), advance_date(timezone.now(), hours=1),
                                          self.airplane1, self.crew1)
        with self.assertRaises(ValidationError):
            self.create_flight(timezone.now(), advance_date(timezone.now(), hours=1),
                                          self.airplane2, self.crew2)