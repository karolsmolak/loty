from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F


class Worker(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return "{} {} (id: {})".format(self.name, self.surname, self.id)


class Crew(models.Model):
    workers = models.ManyToManyField(Worker, related_name='crews')
    captain = models.ForeignKey(Worker, on_delete=models.CASCADE)

    def clean(self):
        if self.captain not in self.workers.all():
            raise ValidationError("Captain must be in workers")
        for flight in self.flights.all():
            for concurrent_flight in flight.get_concurrent_flights():
                if (flight.crew.workers.all() & concurrent_flight.crew.workers.all()).exists():
                    raise ValidationError("Członek załogi nie może być jednocześnie na dwóch lotach: {} i {}".format(flight.pk, concurrent_flight.pk))
        super().clean()

    def __str__(self):
        return "Załoga nr {}, kapitan {}".format(self.pk, str(self.captain))
