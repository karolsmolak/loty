from django.core.exceptions import ValidationError
from django.db import models, connection
from django.db.models import F, QuerySet


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

        #Ewentualnie tak, nie widze jak to można w miare łatwo w orm zrobić :(
        with connection.cursor() as cursor:
            cursor.execute("""
             SELECT a.id first_id, b.id second_id
             FROM (SELECT f.id, f.crew_id, f.start, f.landing FROM flights_flight f WHERE f.crew_id = %s) a, flights_flight b
             JOIN crews_crew_workers workercrew_a ON workercrew_a.crew_id = a.crew_id
             JOIN crews_crew_workers workercrew_b ON workercrew_b.crew_id = b.crew_id
             WHERE ((a.start <= b.start AND a.landing >= b.start)
             OR (a.start >= b.start AND b.landing >= a.start))
             AND a.id != b.id
             AND workercrew_a.worker_id = workercrew_b.worker_id""", [self.id])
            conflicts = cursor.fetchall()
            if conflicts:
               raise ValidationError(
                   "Członek załogi nie może być jednocześnie na dwóch lotach: {} i {}".format(conflicts[0][0],
                                                                                              conflicts[0][1]))
        super().clean()

    def __str__(self):
        return "Załoga nr {}, kapitan {}".format(self.pk, str(self.captain))
