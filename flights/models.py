from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone

from crews.models import Crew


class Passenger(models.Model):
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)

    def __str__(self):
        return "{} {}".format(self.name, self.surname)

    class Meta:
        unique_together = ('name', 'surname')
        ordering = ['surname', 'name']


class Airplane(models.Model):
    registration_number = models.CharField(max_length=30, unique=True)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(20)])

    def __str__(self):
        return self.registration_number

    class Meta:
        ordering = ['registration_number']


class Flight(models.Model):
    start = models.DateTimeField()
    start_airport = models.CharField(max_length=30)
    landing = models.DateTimeField()
    landing_airport = models.CharField(max_length=30)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name="flights")
    passengers = models.ManyToManyField(Passenger, related_name="flights", through='Ticket')
    crew = models.ForeignKey(Crew, related_name='flights', on_delete=models.CASCADE);

    @property
    def duration(self):
        return self.landing - self.start

    @property
    def booked_seats(self):
        return self.get_booked_seats(None)

    class Meta:
        ordering = ['start']

    def get_booked_seats(self, except_for):
        seats_taken = self.ticket_set.exclude(pk=except_for).aggregate(Sum('count'))['count__sum']
        return seats_taken if seats_taken else 0

    def get_absolute_url(self):
        return reverse('flight_details', args=[str(self.pk)])

    def get_concurrent_flights(self):
        return (Flight.objects.filter(start__gte=self.start,
                                      landing__lte=self.start) |
                Flight.objects.filter(start__lte=self.start,
                                      landing__gte=self.start)).exclude(pk=self.pk)

    def clean(self):
        self.check_if_flight_has_minimum_duration()
        self.check_if_airplane_not_already_assigned()
        self.check_airplane_not_too_much_flights_per_day()
        self.check_crew_members_not_already_assigned()
        super().clean()

    def check_if_flight_has_minimum_duration(self):
        if self.duration < timezone.timedelta(minutes=30):
            raise ValidationError("Lot nie może trwać < 30 minut")

    def check_if_airplane_not_already_assigned(self):
        if self.get_concurrent_flights().filter(airplane=self.airplane).exists():
            raise ValidationError("Samolot nie może obsługiwać jednocześnie dwóch lotów")

    def check_airplane_not_too_much_flights_per_day(self):
        day = timezone.timedelta(days=1)
        flights = list(self.airplane.flights.filter(start__gte=self.start - day,
                                                    start__lte=self.start + day)
                       .exclude(pk=self.pk))
        if len(flights) >= 4:
            for i in range(0, len(flights) - 3):
                if flights[i + 3].start - flights[i].start < day:
                    raise ValidationError("Samolot może mieć co najwyżej 4 loty dziennie")

    def check_crew_members_not_already_assigned(self):
        concurrent_flights = self.get_concurrent_flights()
        for worker in self.crew.workers.all():
            for flight in concurrent_flights:
                if worker in flight.crew.workers.all():
                    raise ValidationError("Członek załogi nie może być jednocześnie na dwóch lotach")


    def __str__(self):
        return "Lot nr {}".format(self.pk)


class Ticket(models.Model):
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    count = models.PositiveIntegerField()

    def clean(self):
        seats_taken = self.flight.get_booked_seats(self.pk)
        if seats_taken + self.count > self.flight.airplane.capacity:
            raise ValidationError({"count": "Nie można zarezerwować biletu ze względu na brak miejsc."})
        return super().clean()

    class Meta:
        unique_together = ('passenger', 'flight')
        ordering = ['passenger']

    def __str__(self):
        return "{}, {} - {} miejsc".format(str(self.passenger), str(self.flight), self.count)