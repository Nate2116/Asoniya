from django.contrib import admin
from .models import Destination, Attraction, Accommodation, CarRental, TravelAgency, Trip

# Register your models here to make them visible in the admin panel
admin.site.register(Destination)
admin.site.register(Attraction)
admin.site.register(Accommodation)
admin.site.register(CarRental)
admin.site.register(TravelAgency)
admin.site.register(Trip)