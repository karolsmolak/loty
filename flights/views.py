from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView

from .forms import DateFilter, TicketForm
from .models import Flight


class FlightList(ListView):
    template_name = 'homepage.html'
    model = Flight
    context_object_name = 'flights'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = DateFilter(self.request.GET)
        if form.is_valid():
            context['form'] = form
        else:
            context['form'] = DateFilter()
        return context

    def get_queryset(self):
        form = DateFilter(self.request.GET)
        if form.is_valid():
            date = form.cleaned_data['date']
            return Flight.objects.filter(start__date=date)
        return Flight.objects.all()


class FlightDetails(DetailView):
    model = Flight
    template_name = 'details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TicketForm()
        flight = self.get_object()
        context['flight'] = flight
        context['seats_taken'] = flight.get_booked_seats(except_for=None)
        context['passengers'] = flight.ticket_set.values('count',
                                                         name=F('passenger__name'),
                                                         surname=F('passenger__surname')).all()
        return context

    @method_decorator(login_required)
    def post(self, request, pk):
        self.object = self.get_object()
        form = TicketForm(request.POST)
        if form.is_valid():
            form.book_ticket(flight=self.object)
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context=context)


def logout_page(request):
    logout(request)
    return HttpResponseRedirect(request.GET.get('next', '/'))
