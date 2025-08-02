from django.db import models
from django.contrib.auth.models import User

class Destination(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='destination_images/', null=True, blank=True)

    def __str__(self):
        return self.name

class Attraction(models.Model):
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='attractions')
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='attraction_images/', null=True, blank=True)

    def __str__(self):
        return self.name

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
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='car_rental_images/', null=True, blank=True)
    def __str__(self): 
        return self.name

class TravelAgency(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='travel_agency_images/', null=True, blank=True)
    def __str__(self):
        return self.name

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
    travel_agencies = models.ManyToManyField(TravelAgency, blank=True)
    attractions = models.ManyToManyField(Attraction, blank=True)

    def __str__(self):
        return f"{self.name} for {self.user.username} ({self.status})"