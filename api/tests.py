from django.utils import timezone

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from crews.models import Worker, Crew
from flights.models import Flight, Airplane


def get_crew_worker_url(flight, worker):
    return reverse('crew', kwargs={
        'flight_id': flight.pk,
        'worker_id': worker.pk
    })


def get_flight_url(flight):
    return '/api/flights/{}'.format(flight.pk)


class ApiTests(APITestCase):

    def setUp(self):
        airplane1 = Airplane.objects.create(registration_number="samolocik", capacity=40)
        airplane2 = Airplane.objects.create(registration_number="samolocik1", capacity=40)
        self.user = User.objects.create(username="user1", password="secret")
        self.worker1 = Worker.objects.create(name="worker1", surname="worker1")
        self.worker2 = Worker.objects.create(name="worker2", surname="worker2")
        self.worker3 = Worker.objects.create(name="worker3", surname="worker3")
        self.worker4 = Worker.objects.create(name="worker4", surname="worker4")
        self.crew = Crew.objects.create(captain=self.worker1)
        self.crew.workers.add(self.worker1, self.worker2)
        self.crew1 = Crew.objects.create(captain=self.worker4)
        self.crew1.workers.add(self.worker4)
        self.flight1 = Flight.objects.create(crew=self.crew,
                                             start=timezone.now(),
                                             landing=timezone.now() + timezone.timedelta(hours=1),
                                             start_airport="start",
                                             landing_airport="finish",
                                             airplane=airplane1)
        self.flight2 = Flight.objects.create(crew=self.crew1,
                                             start=timezone.now(),
                                             landing=timezone.now() + timezone.timedelta(hours=1),
                                             start_airport="start",
                                             landing_airport="finish",
                                             airplane=airplane2)

    def test_delete_crew_member(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.delete(get_crew_worker_url(self.flight1, self.worker2)).status_code,
                         status.HTTP_200_OK)
        self.assertFalse(self.worker2 in self.crew.workers.all())

    def test_delete_captain_should_fail(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.delete(get_crew_worker_url(self.flight1, self.worker1)).status_code,
                         status.HTTP_400_BAD_REQUEST)
        self.assertTrue(self.worker1 in self.crew.workers.all())
        self.assertTrue(self.crew.captain == self.worker1)

    def test_add_crew_member(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.post(get_crew_worker_url(self.flight1, self.worker3)).status_code,
                         status.HTTP_200_OK)
        self.assertTrue(self.worker3 in self.flight1.crew.workers.all())

    def test_add_crew_member_two_concurrent_flights(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.post(get_crew_worker_url(self.flight2, self.worker2)).status_code,
                         status.HTTP_409_CONFLICT)
        self.assertFalse(self.worker2 in self.flight2.crew.workers.all())

    def test_add_crew_member_duplicate_should_fail(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.post(get_crew_worker_url(self.flight1, self.worker2)).status_code,
                         status.HTTP_409_CONFLICT)

    def test_change_captain(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.put(get_crew_worker_url(self.flight1, self.worker2)).status_code,
                         status.HTTP_200_OK)
        self.crew.refresh_from_db()
        self.assertEqual(self.crew.captain.pk, self.worker2.pk)

    def test_change_captain_not_in_crew(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.put(get_crew_worker_url(self.flight1, self.worker3)).status_code,
                         status.HTTP_404_NOT_FOUND)
        self.crew.refresh_from_db()
        self.assertFalse(self.crew.captain == self.worker3)
