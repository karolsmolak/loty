from django import forms
from django.core.validators import MinValueValidator


class DateInput(forms.DateInput):
    input_type = 'date'


class PassengerForm(forms.Form):
    name = forms.CharField(label='Imię', max_length=30)
    surname = forms.CharField(label='Nazwisko', max_length=30)
    count = forms.IntegerField(label="Ilość biletów", validators=[MinValueValidator(1)])


class DateFilter(forms.Form):
    date = forms.DateField(label="Data wylotu", widget=forms.DateInput(attrs={'type': 'date'}))
