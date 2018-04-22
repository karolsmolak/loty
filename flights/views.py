from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth import logout
from .forms import PassengerForm, DateFilter
from .models import Flight, Passenger, Ticket
from django.db import transaction
from django.core.exceptions import ValidationError


def get_flight(flight_id):
    try:
        return Flight.objects.get(pk=flight_id)
    except Flight.DoesNotExist:
        raise Http404


def index(request):
    flights = list(Flight.objects.values())
    form = DateFilter(request.GET)
    if form.is_valid():
        flights = list(Flight.objects.filter(start__date=form.cleaned_data['date']).values())
        return render(request, 'homepage.html', {'flights': flights,
                                                 'filter': DateFilter(),
                                                 'date': form.cleaned_data['date']})
    return render(request, 'homepage.html', {'flights': flights,
                                             'filter': DateFilter()})


def flight_details(request, flight_id):
    flight = get_flight(flight_id)
    seats_taken = flight.get_booked_seats(None)
    flights = list(Flight.objects.values())
    passengers = flight.ticket_set.values('count',
                                          name=F('passenger__name'),
                                          surname=F('passenger__surname')).all()
    return render(request, 'details.html', {'form': PassengerForm(),
                                            'flights': flights,
                                            'flight': flight,
                                            'seats_taken': seats_taken,
                                            'passengers': passengers})


@login_required
@transaction.atomic
def add_passenger(request, flight_id):
    form = PassengerForm(request.POST)
    if form.is_valid():
        flight = get_flight(flight_id)
        passenger, created = Passenger.objects.get_or_create(name=form.cleaned_data['name'],
                                                             surname=form.cleaned_data['surname'])
        ticket = Ticket.objects.filter(flight=flight).select_for_update().filter(passenger=passenger).first()
        if ticket:
            ticket.count += form.cleaned_data['count']
            ticket.save(update_fields=['count'])
        else:
            ticket = Ticket.objects.create(passenger=passenger, flight=flight,
                                           count=form.cleaned_data['count'])
        try:
            ticket.full_clean()
        except ValidationError:
            transaction.set_rollback(True)
    return redirect('flight_details', flight_id)


def logout_page(request):
    logout(request)
    return HttpResponseRedirect(request.GET.get('next', '/'))
