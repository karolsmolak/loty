from rest_framework import serializers

from crews.models import Crew, Worker
from flights.models import Flight


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ('captain', 'workers')


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = ('id', 'name', 'surname')


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ('id', 'start', 'landing', 'booked_seats', 'start_airport',
                  'landing_airport', 'airplane', 'passengers', 'crew')
        depth = 2
