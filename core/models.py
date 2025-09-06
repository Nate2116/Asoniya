from django.db import models
from django.contrib.auth.models import User

class CarouselImage(models.Model):
    image = models.ImageField(upload_to='carousel_images/')
    title = models.CharField(max_length=200, blank=True, null=True)
    caption = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return self.title or "Carousel Image"
    
class Destination(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='destination_images/', null=True, blank=True, verbose_name="Cover Image")

    def __str__(self):
        return self.name
    
class Attraction(models.Model):
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='attractions')
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='attraction_images/', null=True, blank=True, verbose_name="Cover Image")

    def __str__(self):
        return self.name

class AttractionImage(models.Model):
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='attraction_gallery/')

    def __str__(self):
        return f"Image for {self.attraction.name}"

class Accommodation(models.Model):
    ACCOMMODATION_TYPES = [('Hotel', 'Hotel'), ('Resort', 'Resort'), ('Lodge', 'Lodge')]

    # This new field links Accommodation to a Destination for filtering
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='accommodations')
    name = models.CharField(max_length=100)
    description = models.TextField()
    accommodation_type = models.CharField(max_length=10, choices=ACCOMMODATION_TYPES, default='Hotel')
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=2, decimal_places=1, help_text="Rating from 1.0 to 5.0")
    image = models.ImageField(upload_to='accommodation_images/', null=True, blank=True)

    def __str__(self):
        return self.name

# Add other models like CarRental, TravelAgency, and Trip here as needed...

class CarRental(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='car_rental_images/', null=True, blank=True,  verbose_name="Cover Image")
    def __str__(self): 
        return self.name

class Car(models.Model):
    rental_company = models.ForeignKey(CarRental, on_delete=models.CASCADE, related_name='cars')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='car_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.rental_company.name})"

class CarRentalImage(models.Model):
    rental_company = models.ForeignKey(CarRental, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='car_rental_gallery/')

    def __str__(self):
        return f"Image for {self.rental_company.name}"
    
class TravelAgency(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='travel_agency_images/', null=True, blank=True, verbose_name="Cover Image")
    def __str__(self):
        return self.name
    
class TourPackage(models.Model):
    agency = models.ForeignKey(TravelAgency, on_delete=models.CASCADE, related_name='tours')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()
    image = models.ImageField(upload_to='tour_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.agency.name})"

class TravelAgencyImage(models.Model):
    agency = models.ForeignKey(TravelAgency, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='travel_agency_gallery/')

    def __str__(self):
        return f"Image for {self.agency.name}"

from django.db import models
from django.contrib.auth.models import User

class Trip(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active Plan'),
        ('saved', 'Saved Trip'),
        ('booked', 'Booked Trip'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, default="New Trip Plan")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
    # Date fields for the trip duration
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # All the selected items for the trip
    destinations = models.ManyToManyField(Destination, blank=True)
    accommodations = models.ManyToManyField(Accommodation, blank=True)
    car_rentals = models.ManyToManyField(CarRental, blank=True)
    cars = models.ManyToManyField(Car, blank=True)
    travel_agencies = models.ManyToManyField(TravelAgency, blank=True)
    attractions = models.ManyToManyField(Attraction, blank=True)
    # New: selected tour packages from travel agencies
    tour_packages = models.ManyToManyField(TourPackage, blank=True)

    def __str__(self):
        return f"{self.name} for {self.user.username} ({self.status})"