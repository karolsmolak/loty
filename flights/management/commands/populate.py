import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from crews.models import Worker, Crew
from flights.models import Airplane, Flight

airplane_count = 50
flights_per_airplane = 50
min_seats = 20
min_duration = 30
max_day_flights_per_airplane = 4
num_of_workers = 400


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        print("Populating database")
        random.seed()
        Worker.objects.bulk_create([
            Worker(name="Jan", surname="Kowalski nr {}".format(i)) for i in range(1, num_of_workers)
        ])
        for i in range(1, airplane_count):
            airplane = Airplane.objects.create(registration_number="Samolot nr {}".format(i),
                                               capacity=random.randrange(min_seats, min_seats + 10))
            start_date = timezone.now()
            for j in range(1, flights_per_airplane):
                start, finish = random.sample(range(1, 10), 2)
                landing_date = start_date + timezone.timedelta(minutes=min_duration + random.randrange(100))
                flight = Flight(start=start_date,
                                start_airport="Lotnisko nr {}".format(start),
                                landing=landing_date,
                                landing_airport="Lotnisko nr {}".format(finish),
                                airplane=airplane)

                available_workers = set(range(1, num_of_workers))
                concurrent_flights = flight.get_concurrent_flights()
                for concurrent_flight in concurrent_flights:
                    for worker in concurrent_flight.crew.workers.all():
                        available_workers.discard(worker.pk)

                worker_ids = random.sample(available_workers, 5)
                captain = Worker.objects.get(pk=worker_ids[0])
                crew = Crew.objects.create(captain=captain)
                for worker_id in worker_ids:
                    crew.workers.add(Worker.objects.get(pk=worker_id))
                flight.crew = crew
                flight.save()
                crew.save()

                start_date = landing_date + timezone.timedelta(hours=24 / max_day_flights_per_airplane)
                print("{}%\r".format(int((i * flights_per_airplane + j) / 25)), end='', flush=True)
