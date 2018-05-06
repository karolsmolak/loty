from django.contrib import admin

from .models import Flight, Airplane, Ticket, Passenger


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    date_hierarchy = 'start'
    list_display = ('__str__', 'start_airport', 'landing_airport', 'start', 'landing', 'airplane')


admin.site.register(Airplane)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('pk', 'flight', 'passenger', 'count')


admin.site.register(Passenger)
