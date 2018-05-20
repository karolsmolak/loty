from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from crews.models import Crew, Worker
from .models import Flight, Airplane, Ticket, Passenger


def advance_date(date, hours=0, minutes=0, seconds=0):
    return date + timezone.timedelta(hours=hours, minutes=minutes, seconds=seconds)


class FlightValidationTest(TestCase):
    def create_flight(self, start, landing):
        return Flight.objects.create(start=start,
                                     landing=landing,
                                     airplane=self.airplane,
                                     start_airport="start",
                                     landing_airport="finish",
                                     crew=self.crew).full_clean()

    def setUp(self):
        self.date = timezone.now()
        self.airplane = Airplane.objects.create(registration_number="samolocik", capacity=40)
        worker = Worker.objects.create(name="a", surname="b")
        self.crew = Crew.objects.create(captain=worker)
        self.crew.workers.add(worker)

    def test_creating_airplane_with_at_least_20_seats_shouldnt_fail(self):
        Airplane.objects.create(registration_number="big enough airplane",
                                capacity=20).full_clean()

    def test_creating_airplane_with_less_than_20_seats_should_fail(self):
        with self.assertRaises(ValidationError):
            Airplane.objects.create(registration_number="small_airplane",
                                    capacity=19).full_clean()

    def test_creating_flight_lasting_less_than_30_minutes_should_fail(self):
        with self.assertRaises(ValidationError):
            self.create_flight(start=self.date,
                               landing=advance_date(self.date, minutes=29, seconds=59))

    def test_creating_flight_lasting_at_least_30_minutes_shouldnt_fail(self):
        self.create_flight(start=self.date,
                           landing=advance_date(self.date, minutes=30))

    def test_add_more_than_4_flights_per_airplane_day_should_fail(self):
        for i in range(0, 5):
            if i < 4:
                self.create_flight(start=advance_date(self.date, hours=5 * i),
                                   landing=advance_date(self.date, hours=5 * i + 1))
            else:
                with self.assertRaises(ValidationError):
                    self.create_flight(start=advance_date(self.date, hours=5 * i),
                                       landing=advance_date(self.date, hours=5 * i + 1))

    def test_add_more_than_4_flights_per_airplane_not_same_day_shouldnt_fail(self):
        for i in range(0, 10):
            self.create_flight(start=advance_date(self.date, hours=7 * i),
                               landing=advance_date(self.date, hours=7 * i + 1))

    def test_assigning_airplane_to_two_simultaneous_flights_should_fail(self):
        self.create_flight(start=self.date,
                           landing=advance_date(self.date, minutes=60))
        with self.assertRaises(ValidationError):
            self.create_flight(start=advance_date(self.date, minutes=30),
                               landing=advance_date(self.date, minutes=90))


class TicketValidationTest(TestCase):
    def create_flight(self, start, landing):
        return Flight.objects.create(start=start,
                                     landing=landing,
                                     airplane=self.airplane,
                                     start_airport="start",
                                     landing_airport="finish",
                                     crew=self.crew)

    def setUp(self):
        worker = Worker.objects.create(name="a", surname="b")
        self.crew = Crew.objects.create(captain=worker)
        self.crew.workers.add(worker)
        self.airplane = Airplane.objects.create(registration_number="samolocik",
                                                capacity=20)
        self.flight = self.create_flight(timezone.now(), timezone.now())
        self.passenger1 = Passenger.objects.create(name='name1',
                                                   surname='surname1')
        self.passenger2 = Passenger.objects.create(name='name2',
                                                   surname='surname2')

    def test_booking_over_seat_limit_should_fail(self):
        ticket = Ticket(flight=self.flight,
                        count=12,
                        passenger=self.passenger1)
        ticket.full_clean()
        ticket.save()
        with self.assertRaises(ValidationError):
            Ticket.objects.create(flight=self.flight,
                                  count=9,
                                  passenger=self.passenger2).full_clean()
