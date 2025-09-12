from django.contrib import admin
from .models import (
    CarouselImage, Destination, Attraction, AttractionImage, Accommodation, 
    AccommodationGalleryImage, RoomType,
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

class AccommodationGalleryImageInline(admin.TabularInline):
    model = AccommodationGalleryImage
    extra = 3  # Show 3 empty forms for gallery images

class RoomTypeInline(admin.TabularInline):
    model = RoomType
    extra = 1  # Show 1 empty form for a room type

class AccommodationAdmin(admin.ModelAdmin):
    inlines = [AccommodationGalleryImageInline, RoomTypeInline]
    list_display = ('name', 'destination', 'accommodation_type')
    list_filter = ('destination', 'accommodation_type')
    search_fields = ('name', 'description')

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
admin.site.register(Accommodation, AccommodationAdmin)
admin.site.register(CarRental, CarRentalAdmin)
admin.site.register(TravelAgency, TravelAgencyAdmin)
admin.site.register(Trip)