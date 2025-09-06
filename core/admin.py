from django.contrib import admin
from .models import (
    CarouselImage, Destination, Attraction, AttractionImage, Accommodation, 
    CarRental, Car, CarRentalImage, 
    TravelAgency, TourPackage, TravelAgencyImage, Trip
)

# --- Admin for Carousel Images (New) ---
class CarouselImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'caption')

# --- Inlines for Destinations (New) ---

class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name',)

# --- Inlines for Attractions (New) ---
class AttractionImageInline(admin.TabularInline):
    model = AttractionImage
    extra = 2

class AttractionAdmin(admin.ModelAdmin):
    inlines = [AttractionImageInline]
    list_display = ('name', 'destination')

class TourPackageInline(admin.TabularInline):
    model = TourPackage
    extra = 1

class TravelAgencyImageInline(admin.TabularInline):
    model = TravelAgencyImage
    extra = 2

class TravelAgencyAdmin(admin.ModelAdmin):
    inlines = [TravelAgencyImageInline, TourPackageInline]
    list_display = ('name', 'description')


class CarInline(admin.TabularInline):
    model = Car
    extra = 1  # How many extra empty forms to show

class CarRentalImageInline(admin.TabularInline):
    model = CarRentalImage
    extra = 2 # Show 2 extra forms for uploading images

# Define the admin class for CarRental
class CarRentalAdmin(admin.ModelAdmin):
    inlines = [
        CarRentalImageInline,
        CarInline,
    ]
    list_display = ('name', 'description')

# Register your models here to make them visible in the admin panel
admin.site.register(CarouselImage, CarouselImageAdmin)
admin.site.register(Destination, DestinationAdmin)
admin.site.register(Attraction, AttractionAdmin)
admin.site.register(Accommodation)
admin.site.register(CarRental, CarRentalAdmin)
admin.site.register(TravelAgency, TravelAgencyAdmin)
admin.site.register(Trip)