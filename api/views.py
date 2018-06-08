# Create your views here.
import json

from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import FlightSerializer, WorkerSerializer
from crews.models import Worker
from flights.models import Flight


class FlightViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer


class WorkersViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer


class CrewView(APIView):
    """
    post:
    Adds worker (id = worker_id) to flight's (id = flight_id) crew

    delete:
    Deletes worker (id = worker_id) to flight's (id = flight_id) crew.
    Deleted worker cant be a captain of flight's crew.

    put:
    Makes a captain from worker (id = worker_id). Previous captain loses his/her status.
    Worker should already be assigned to flight, otherwise 400 will be returned.
    """

    @transaction.atomic
    def post(self, request, flight_id, worker_id):
        flight = get_object_or_404(Flight, pk=flight_id)
        worker = get_object_or_404(Worker, pk=worker_id)
        if worker in flight.crew.workers.all():
            return Response(status=status.HTTP_409_CONFLICT)
        flight.crew.workers.add(worker)
        try:
            flight.crew.full_clean()
        except ValidationError as e:
            transaction.set_rollback(True)
            return Response(data={"error" : e.error_dict['__all__'][0].message}, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, flight_id, worker_id):
        flight = get_object_or_404(Flight, pk=flight_id)
        worker = get_object_or_404(Worker, pk=worker_id)
        if flight.crew.captain == worker:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        flight.crew.workers.remove(worker)
        flight.crew.save()
        return Response(status=status.HTTP_200_OK)

    def put(self, request, flight_id, worker_id):
        flight = get_object_or_404(Flight, pk=flight_id)
        worker = get_object_or_404(Worker, pk=worker_id)
        if not flight.crew.workers.filter(pk=worker.pk).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        flight.crew.captain = worker
        flight.crew.save()
        return Response(status=status.HTTP_200_OK)
