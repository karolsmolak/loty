from django.contrib import admin

from .models import Flight, Airplane, Ticket, Passenger


# Register your models here.
class FlightAdmin(admin.ModelAdmin):
    date_hierarchy = 'start'
    list_display = ('__str__', 'start_airport', 'landing_airport', 'start', 'landing')


admin.site.register(Flight, FlightAdmin)
admin.site.register(Airplane)
admin.site.register(Ticket)
admin.site.register(Passenger)
