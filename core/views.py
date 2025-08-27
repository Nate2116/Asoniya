# core/views.py

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Destination, Attraction, AttractionImage, Accommodation, CarRental, Car, CarRentalImage, TravelAgency, TourPackage, TravelAgencyImage, Trip
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import json

# ===============================================
# PAGE RENDERING VIEWS
# ===============================================

def index_page(request):
    return render(request, 'index.html')

def destinations_page(request):
    context = {'destinations': Destination.objects.all()}
    return render(request, 'destinations.html', context)

def destination_detail_page(request, destination_id):
    destination = get_object_or_404(Destination, id=destination_id)
    context = {
        'destination': destination,
    }
    return render(request, 'destination_detail.html', context)

def attraction_detail_page(request, attraction_id):
    attraction = get_object_or_404(Attraction, id=attraction_id)
    context = {
        'attraction': attraction,
    }
    return render(request, 'attraction_detail.html', context)

def accommodation_page(request):
    context = {'destinations': Destination.objects.all()}
    return render(request, 'accommodation.html', context)

def travel_agencies_page(request):
    return render(request, 'travel-agencies.html')

def travel_agency_detail_page(request, agency_id):
    agency = get_object_or_404(TravelAgency, id=agency_id)
    context = {
        'agency': agency,
    }
    return render(request, 'travel_agency_detail.html', context)

def car_rentals_page(request):
    return render(request, 'car-rentals.html')

def car_rental_detail_page(request, rental_id):
    rental_company = get_object_or_404(CarRental, id=rental_id)
    context = {
        'company': rental_company,
    }
    return render(request, 'car_rental_detail.html', context)

def profile_page(request):
    return render(request, 'profile.html')
    
def trip_summary_page(request):
    return render(request, 'trip-summary.html')

def view_saved_trip_page(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    
    duration = None
    if trip.start_date and trip.end_date:
        delta = trip.end_date - trip.start_date
        duration = delta.days + 1

    # --- THIS IS THE FIX ---
    # The total cost should be calculated from the prices of individual cars,
    # not from the CarRental company model.
    total_cost = 0
    for item in trip.accommodations.all():
        total_cost += item.price_per_night
    # Sum the price of each selected car
    for item in trip.cars.all():
        if item.price_per_day:
            total_cost += item.price_per_day

    context = {
        'trip': trip,
        'duration_days': duration,
        'attractions': list(trip.attractions.all()),
        'accommodations': list(trip.accommodations.all()),
        'car_rentals': list(trip.car_rentals.all()),
        'cars': list(trip.cars.all()),
        'travel_agencies': list(trip.travel_agencies.all()),
        'total_cost': total_cost,
    }
    return render(request, 'trip-summary.html', context)

def terms_conditions_page(request):
    return render(request, 'terms-conditions.html')

def privacy_policy_page(request):
    return render(request, 'privacy-policy.html')

def signup_page(request):
    return render(request, 'signup.html')

def login_page(request):
    return render(request, 'login.html')

# ===============================================
# API VIEWS - For fetching data with JavaScript
# ===============================================

def attraction_list_api(request, destination_id):
    attractions = Attraction.objects.filter(destination_id=destination_id)
    data = [{'id': attr.id, 'name': attr.name, 'description': attr.description, 'image_url': attr.image.url if attr.image else None} for attr in attractions]
    return JsonResponse(data, safe=False)

def accommodation_list_api(request):
    queryset = Accommodation.objects.all()
    if destination_id := request.GET.get('destination'):
        queryset = queryset.filter(destination_id=destination_id)
    if acc_type := request.GET.get('type'):
        queryset = queryset.filter(accommodation_type=acc_type)
    if max_price := request.GET.get('max_price'):
        queryset = queryset.filter(price_per_night__lte=max_price)
    if min_rating := request.GET.get('min_rating'):
        queryset = queryset.filter(rating__gte=min_rating)
    
    data = [{'id': item.id, 'name': item.name, 'description': item.description, 'price_per_night': str(item.price_per_night), 'rating': str(item.rating), 'image_url': item.image.url if item.image else None} for item in queryset]
    return JsonResponse(data, safe=False)

def travel_agency_list_api(request):
    agencies = TravelAgency.objects.all()
    data = [{'id': item.id, 'name': item.name, 'description': item.description, 'image_url': item.image.url if item.image else None} for item in agencies]
    return JsonResponse(data, safe=False)

def car_rental_list_api(request):
    cars = CarRental.objects.all()
    data = [{'id': item.id, 'name': item.name, 'description': item.description, 'image_url': item.image.url if item.image else None} for item in cars]
    return JsonResponse(data, safe=False)

# ===============================================
# USER & TRIP API VIEWS
# ===============================================

@csrf_exempt
def signup_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if not username or not password:
            return JsonResponse({'error': 'Username and password are required.'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists.'}, status=400)

        user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        login(request, user)
        return JsonResponse({'status': 'success', 'message': 'User created and logged in.'}, status=201)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def login_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'status': 'success', 'message': 'Login successful.'})
        else:
            return JsonResponse({'error': 'Invalid username or password.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def logout_api(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'status': 'success', 'message': 'Logout successful.'})
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@login_required
def add_to_trip_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item_id = data.get('item_id')
        item_type = data.get('item_type')

        if not item_id or not item_type:
            return JsonResponse({'error': 'Missing item ID or type'}, status=400)

        # Get or create an active trip for the user
        trip, created = Trip.objects.get_or_create(user=request.user, status='active')

        try:
            if item_type == 'destination':
                item = Destination.objects.get(id=item_id)
                trip.destinations.add(item)
            elif item_type == 'attraction':
                item = Attraction.objects.get(id=item_id)
                trip.attractions.add(item)
            elif item_type == 'accommodation':
                item = Accommodation.objects.get(id=item_id)
                trip.accommodations.add(item)
            elif item_type == 'car_rental':
                item = CarRental.objects.get(id=item_id)
                trip.car_rentals.add(item)
            elif item_type == 'car':
                item = Car.objects.get(id=item_id)
                trip.cars.add(item)
            elif item_type == 'travel_agency':
                item = TravelAgency.objects.get(id=item_id)
                trip.travel_agencies.add(item)
            elif item_type == 'tour_package':
                item = TourPackage.objects.get(id=item_id)
                trip.tour_packages.add(item)
            else:
                return JsonResponse({'error': 'Invalid item type'}, status=400)
            return JsonResponse({'status': 'success', 'message': f'{item_type.replace("_", " ").title()} added to trip.'})
        except Exception as e:
            return JsonResponse({'error': f'Could not find item. Details: {str(e)}'}, status=404)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@login_required
def get_trip_summary_api(request):
    trip = Trip.objects.filter(user=request.user, status='active').first()
    if not trip:
        return JsonResponse({'error': 'No active trip found.'}, status=404)

    # --- THIS IS THE FIX ---
    # We serialize the selected cars, not the rental companies for the price.
    accommodations = [{'name': acc.name, 'description': acc.description, 'price': acc.price_per_night, 'image_url': acc.image.url if acc.image else ''} for acc in trip.accommodations.all()]
    selected_cars = [{'name': car.name, 'description': car.description, 'price': car.price_per_day, 'image_url': car.image.url if car.image else ''} for car in trip.cars.all()]
    
    # The cost is calculated from accommodations and selected cars.
    total_cost = sum(a['price'] for a in accommodations) + sum(c['price'] for c in selected_cars if c['price'])

    data = {
        'trip_name': trip.name,
        'attractions': [{'name': attr.name, 'description': attr.description, 'image_url': attr.image.url if attr.image else ''} for attr in trip.attractions.all()],
        'accommodations': accommodations,
        'cars': selected_cars, # Send the detailed car list
        'car_rentals': [{'name': cr.name} for cr in trip.car_rentals.all()], # Still useful to know the company
        'travel_agencies': [{'name': agency.name} for agency in trip.travel_agencies.all()],
        'total_cost': total_cost
    }
    return JsonResponse(data)
    
@login_required
def save_trip_api(request):
    if request.method == 'POST':
        try:
            active_trip = Trip.objects.get(user=request.user, status='active')
            first_destination = active_trip.destinations.first()
            if first_destination:
                active_trip.name = f"Trip to {first_destination.name}"
            else:
                active_trip.name = "My Saved Ethiopian Trip"
            active_trip.status = 'saved'
            active_trip.save()
            return JsonResponse({'status': 'success', 'message': 'Trip has been saved to your profile.'})
        except Trip.DoesNotExist:
            return JsonResponse({'error': 'No active trip to save.'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def update_trip_dates_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        trip, created = Trip.objects.get_or_create(user=request.user, status='active')
        trip.start_date = start_date
        trip.end_date = end_date
        trip.save()
        return JsonResponse({'status': 'success', 'message': 'Trip dates updated.'})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def profile_api(request):
    user = request.user
    if request.method == 'GET':
        # Fetch all trips for the user, regardless of status
        all_user_trips = Trip.objects.filter(user=user)

        # Serialize the trip data into a list
        trips_data = []
        for trip in all_user_trips:
            # --- FIXED: Added attractions.count() to the item count ---
            item_count = trip.destinations.count() + trip.attractions.count() + \
                         trip.accommodations.count() + trip.car_rentals.count() + \
                         trip.travel_agencies.count()
            trips_data.append({
                'id': trip.id,
                'name': trip.name,
                'status': trip.get_status_display(),
                'item_count': item_count,
                'view_url': reverse('view_saved_trip', args=[trip.id])
            })

        # Combine personal info and all trips into one response
        data = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'saved_trips': trips_data 
        }
        return JsonResponse(data)
        
    elif request.method == 'POST':
        # This part handles updating the user's profile information.
        data = json.loads(request.body)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.save()
        return JsonResponse({'status': 'success', 'message': 'Profile updated.'})