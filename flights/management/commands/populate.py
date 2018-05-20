import random

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


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        random.seed()
        Worker.objects.bulk_create([
            Worker(name="Jan", surname="Kowalski nr {}".format(i)) for i in range(1, 1000)
        ])
        for i in range(1, airplane_count):
            airplane = Airplane.objects.create(registration_number="Samolot nr {}".format(i),
                                               capacity=random.randrange(min_seats, min_seats + 10))
            start_date = timezone.now()
            airplane_flights = []
            for j in range(1, flights_per_airplane):
                start, finish = random.sample(range(1, 10), 2)
                landing_date = start_date + timezone.timedelta(minutes=min_duration + random.randrange(100))
                captain = Worker.objects.get(pk=random.randrange(1, 1000))
                crew = Crew.objects.create(captain=captain)
                crew.workers.add(captain)
                workers_ids = random.sample(range(1,999), 10)
                for worker_id in workers_ids:
                    if worker_id != captain.id:
                        crew.workers.add(Worker.objects.get(pk=worker_id))
                airplane_flights.append(Flight(start=start_date,
                                               start_airport="Lotnisko nr {}".format(start),
                                               landing=landing_date,
                                               landing_airport="Lotnisko nr {}".format(finish),
                                               airplane=airplane,
                                               crew=crew))
                start_date = landing_date + timezone.timedelta(hours=24 / max_day_flights_per_airplane)
            Flight.objects.bulk_create(airplane_flights)
