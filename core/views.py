# core/views.py

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import CarouselImage, Destination, Attraction, AttractionImage, Accommodation, CarRental, Car, CarRentalImage, TravelAgency, TourPackage, TravelAgencyImage, Trip
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.core.serializers.json import DjangoJSONEncoder
import json

# ===============================================
# PAGE RENDERING VIEWS
# ===============================================

def index_page(request):
    carousel_images = CarouselImage.objects.all()
    context = {
        'carousel_images': carousel_images
    }
    return render(request, 'index.html', context)


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

@login_required
def view_saved_trip_page(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    
    
    # --- Add duration calculation ---
    duration_days = None
    if trip.start_date and trip.end_date:
        delta = trip.end_date - trip.start_date
        duration_days = delta.days + 1

    destinations_data = []
    all_destinations = set()
    for item in list(trip.attractions.all()) + list(trip.accommodations.all()):
        all_destinations.add(item.destination)

    for dest in all_destinations:
        dest_attractions = trip.attractions.filter(destination=dest)
        dest_accommodations = trip.accommodations.filter(destination=dest)
        destinations_data.append({
            'name': dest.name,
            'attractions': [{'name': attr.name, 'description': attr.description, 'image_url': attr.image.url if attr.image else ''} for attr in dest_attractions],
            'accommodations': [{'name': acc.name, 'description': acc.description, 'price': acc.price_per_night, 'image_url': acc.image.url if acc.image else ''} for acc in dest_accommodations]
        })
    
    total_cost = 0
    for item in trip.accommodations.all():
        total_cost += item.price_per_night
    for item in trip.cars.all():
        total_cost += item.price_per_day
    for item in trip.tour_packages.all():
        total_cost += item.price

    trip_data = {
        'trip_name': trip.name,
        'is_saved_trip': True,
        'duration_days': duration_days,
        'destinations': destinations_data,
        'cars': [{'name': car.name, 'description': car.description, 'price': car.price_per_day, 'image_url': car.image.url if car.image else ''} for car in trip.cars.all()],
        'car_rentals': [{'name': cr.name, 'description': cr.description, 'image_url': cr.image.url if cr.image else ''} for cr in trip.car_rentals.all()],
        'travel_agencies': [{'name': agency.name, 'description': agency.description, 'image_url': agency.image.url if agency.image else ''} for agency in trip.travel_agencies.all()],
        'tour_packages': [{'name': tour.name, 'description': tour.description, 'price': tour.price, 'image_url': tour.image.url if tour.image else ''} for tour in trip.tour_packages.all()],
        'total_cost': total_cost,
    }

    context = {
        'trip_json': json.dumps(trip_data, cls=DjangoJSONEncoder),
        'start_date': trip.start_date,
        'end_date': trip.end_date,
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

    duration_days = None
    if trip.start_date and trip.end_date:
        delta = trip.end_date - trip.start_date
        duration_days = delta.days + 1

    if not trip:
        return JsonResponse({'error': 'No active trip found.'}, status=404)

    # --- New Organized Structure ---
    destinations_data = []
    # Get all unique destinations from the selected attractions and accommodations
    all_destinations = set()
    for item in list(trip.attractions.all()) + list(trip.accommodations.all()):
        all_destinations.add(item.destination)

    for dest in all_destinations:
        dest_attractions = trip.attractions.filter(destination=dest)
        dest_accommodations = trip.accommodations.filter(destination=dest)
        destinations_data.append({
            'name': dest.name,
            'attractions': [{'name': attr.name, 'description': attr.description, 'image_url': attr.image.url if attr.image else ''} for attr in dest_attractions],
            'accommodations': [{'name': acc.name, 'description': acc.description, 'price': acc.price_per_night, 'image_url': acc.image.url if acc.image else ''} for acc in dest_accommodations]
        })

    selected_cars = [{'name': car.name, 'description': car.description, 'price': car.price_per_day, 'image_url': car.image.url if car.image else ''} for car in trip.cars.all()]
    tour_packages = [{'name': tour.name, 'description': tour.description, 'price': tour.price, 'image_url': tour.image.url if tour.image else ''} for tour in trip.tour_packages.all()]
    
    # Calculate total cost from all priced items
    total_cost = sum(acc['price'] for dest in destinations_data for acc in dest['accommodations']) \
               + sum(c['price'] for c in selected_cars if c['price']) \
               + sum(t['price'] for t in tour_packages if t['price'])

    data = {
        'trip_name': trip.name,
        'start_date': trip.start_date.strftime('%b %d, %Y') if trip.start_date else None,
        'end_date': trip.end_date.strftime('%b %d, %Y') if trip.end_date else None,
        'duration_days': duration_days,
        'destinations': destinations_data,
        'cars': selected_cars,
        'car_rentals': [{'name': cr.name, 'description': cr.description, 'image_url': cr.image.url if cr.image else ''} for cr in trip.car_rentals.all()],
        'travel_agencies': [{'name': agency.name, 'description': agency.description, 'image_url': agency.image.url if agency.image else ''} for agency in trip.travel_agencies.all()],
        'tour_packages': tour_packages,
        'total_cost': total_cost
    }
    return JsonResponse(data)
    
@login_required
def save_trip_api(request):
    if request.method == 'POST':
        trip = get_object_or_404(Trip, user=request.user, status='active')
        
        # New Naming Logic
        trip_name = "My Ethiopian Adventure"
        attraction = trip.attractions.first()
        if attraction:
            trip_name = f"Trip to {attraction.name}"
        
        if trip.start_date:
            trip_name += f" on {trip.start_date.strftime('%b %d, %Y')}"

        trip.name = trip_name
        trip.status = 'saved'
        trip.save()
        return JsonResponse({'status': 'success', 'message': 'Trip has been saved to your profile.'})
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
        # --- This is the fix ---
        # Fetch all trips for the user, ordering by the most recent first.
        all_user_trips = Trip.objects.filter(user=user).order_by('-id')

        # Serialize the trip data into a list
        trips_data = []
        for trip in all_user_trips:
            trips_data.append({
                'id': trip.id,
                'name': trip.name,
                'status': trip.get_status_display(),
                'start_date': trip.start_date.strftime('%b %d, %Y') if trip.start_date else None,
                'end_date': trip.end_date.strftime('%b %d, %Y') if trip.end_date else None,
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