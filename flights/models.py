from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Passenger(models.Model):
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)

    def __str__(self):
        return self.surname + " " + self.name

    class Meta:
        unique_together = ('name', 'surname')
        ordering = ['surname', 'name']


class Airplane(models.Model):
    registration_number = models.CharField(max_length=30, primary_key=True)
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
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    passengers = models.ManyToManyField(Passenger, related_name="flights", through='Ticket')

    class Meta:
        ordering = ['start']

    def get_booked_seats(self, except_for):
        seats_taken = self.ticket_set.exclude(pk=except_for).aggregate(Sum('count'))['count__sum']
        return seats_taken if seats_taken else 0

    def clean(self):
        self.check_if_flight_has_minimum_duration()
        self.check_if_airplane_not_already_assigned()
        self.check_airplane_not_too_much_flights_per_day()

    def check_if_flight_has_minimum_duration(self):
        if self.landing - self.start < timezone.timedelta(minutes=30):
            raise ValidationError("Lot nie może trwać < 30 minut")

    def check_if_airplane_not_already_assigned(self):
        if Flight.objects.filter(airplane=self.airplane,
                                 start__gte=self.start,
                                 landing__lte=self.start).count() > 1 or \
                Flight.objects.filter(airplane=self.airplane,
                                      start__lte=self.start,
                                      landing__gte=self.start).count() > 1:
            raise ValidationError("Airplane can't simultaneously be on two flights")

    def check_airplane_not_too_much_flights_per_day(self):
        if Flight.objects.filter(airplane=self.airplane).count() > 4:
            raise ValidationError("Airplane can only be assigned to maximum 4 flights per day")

    def __str__(self):
        return "Lot nr {}".format(self.pk)


class Ticket(models.Model):
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    count = models.PositiveIntegerField()

    def clean(self):
        seats_taken = self.flight.get_booked_seats(self.pk)
        if seats_taken + self.count > self.flight.airplane.capacity:
            raise ValidationError("Nie można zarezerwować biletu ze względu na brak miejsc")

    class Meta:
        unique_together = ('passenger', 'flight')
        ordering = ['passenger']
