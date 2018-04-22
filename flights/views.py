from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views import View

from .forms import PassengerForm, DateFilter
from .models import Flight, Passenger, Ticket


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


class FlightDetails(View):

    def render_detail_page(self, request, flight_id, form=None):
        if not form:
            form = PassengerForm()
        flight = get_object_or_404(Flight, pk=flight_id)
        seats_taken = flight.get_booked_seats(except_for=None)
        flights = list(Flight.objects.values())
        passengers = flight.ticket_set.values('count',
                                              name=F('passenger__name'),
                                              surname=F('passenger__surname')).all()
        return render(request, 'details.html', {'form': form,
                                                'flights': flights,
                                                'flight': flight,
                                                'seats_taken': seats_taken,
                                                'passengers': passengers})

    def get(self, request, flight_id):
        return self.render_detail_page(request, flight_id)

    @method_decorator(login_required)
    def post(self, request, flight_id):
        form = PassengerForm(request.POST)
        if form.is_valid():
            flight = get_object_or_404(Flight, pk=flight_id)
            with transaction.atomic():
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
                except ValidationError as exception:
                    transaction.set_rollback(True)
                    form.add_error("count", exception.message_dict["count"])
        return self.render_detail_page(request, flight_id, form)


def logout_page(request):
    logout(request)
    return HttpResponseRedirect(request.GET.get('next', '/'))
