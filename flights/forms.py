from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import transaction

from flights.models import Passenger, Ticket


class TicketForm(forms.Form):
    name = forms.CharField(label='Imię', max_length=30)
    surname = forms.CharField(label='Nazwisko', max_length=30)
    count = forms.IntegerField(label="Ilość biletów", validators=[MinValueValidator(1)])

    @transaction.atomic
    def book_ticket(self, flight):
        passenger, created = Passenger.objects.get_or_create(name=self.cleaned_data['name'],
                                                             surname=self.cleaned_data['surname'])
        ticket = Ticket.objects.filter(flight=flight).select_for_update().filter(passenger=passenger).first()
        if ticket:
            ticket.count += self.cleaned_data['count']
            ticket.save(update_fields=['count'])
        else:
            ticket = Ticket.objects.create(passenger=passenger, flight=flight,
                                           count=self.cleaned_data['count'])
        try:
            ticket.full_clean()
            return ticket
        except ValidationError as exception:
            transaction.set_rollback(True)
            self.add_error("count", exception.message_dict["count"])


class DateFilter(forms.Form):
    date = forms.DateField(label="Data wylotu", widget=forms.DateInput(attrs={'type': 'date'}))
