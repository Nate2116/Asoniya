# core/views.py

from django.shortcuts import render
from django.http import JsonResponse
from .models import Destination, Accommodation, TravelAgency, CarRental, Attraction, Trip
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json

# ===============================================
# PAGE RENDERING VIEWS
# ===============================================

def index_page(request):
    return render(request, 'index.html')

def destinations_page(request):
    context = {'destinations': Destination.objects.all()}
    return render(request, 'destinations.html', context)

def accommodation_page(request):
    context = {'destinations': Destination.objects.all()}
    return render(request, 'accommodation.html', context)

def travel_agencies_page(request):
    return render(request, 'travel-agencies.html')

def car_rentals_page(request):
    return render(request, 'car-rentals.html')

def profile_page(request):
    return render(request, 'profile.html')
    
def trip_summary_page(request):
    return render(request, 'trip-summary.html')

def terms_conditions_page(request):
    return render(request, 'terms-conditions.html')

def privacy_policy_page(request):
    return render(request, 'privacy-policy.html')

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
    data = [{'id': item.id, 'name': item.name, 'description': item.description, 'price_per_day': str(item.price_per_day), 'image_url': item.image.url if item.image else None} for item in cars]
    return JsonResponse(data, safe=False)

# ===============================================
# USER & TRIP API VIEWS
# ===============================================

@login_required
def add_to_trip_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item_id = data.get('item_id')
        item_type = data.get('item_type')

        if not item_id or not item_type:
            return JsonResponse({'error': 'Missing item ID or type'}, status=400)

        trip, created = Trip.objects.get_or_create(user=request.user)

        try:
            if item_type == 'attraction':
                item = Attraction.objects.get(id=item_id)
                trip.attractions.add(item)
            elif item_type == 'accommodation':
                item = Accommodation.objects.get(id=item_id)
                trip.accommodations.add(item)
            elif item_type == 'car_rental':
                item = CarRental.objects.get(id=item_id)
                trip.car_rentals.add(item)
            elif item_type == 'travel_agency':
                item = TravelAgency.objects.get(id=item_id)
                trip.travel_agencies.add(item)
            else:
                return JsonResponse({'error': 'Invalid item type'}, status=400)
            return JsonResponse({'status': 'success', 'message': f'{item_type} with id {item_id} added to trip.'})
        except Exception as e:
            return JsonResponse({'error': f'Could not find item. Details: {str(e)}'}, status=404)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@login_required
def get_trip_summary_api(request):
    try:
        trip = Trip.objects.get(user=request.user)
        attractions = [{'name': attr.name, 'description': attr.description} for attr in trip.attractions.all()]
        accommodations = [{'name': acc.name} for acc in trip.accommodations.all()]
        car_rentals = [{'name': car.name} for car in trip.car_rentals.all()]
        travel_agencies = [{'name': agency.name} for agency in trip.travel_agencies.all()]
        data = {
            'attractions': attractions,
            'accommodations': accommodations,
            'car_rentals': car_rentals,
            'travel_agencies': travel_agencies,
        }
        return JsonResponse(data)
    except Trip.DoesNotExist:
        return JsonResponse({'error': 'No trip has been started.'}, status=404)

@csrf_exempt
@login_required
def profile_api(request):
    user = request.user
    if request.method == 'GET':
        data = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name, # Ensures first name is included
            'last_name': user.last_name,   # Ensures last name is included
        }
        return JsonResponse(data)
    # The POST logic can remain the same if you add an edit feature later
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

# You will also need signup and login views if they are not already in another file
@csrf_exempt
def signup_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if not username or not password:
            return JsonResponse({'error': 'Username and password are required.'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists.'}, status=400)

        user = User.objects.create_user(username=username, password=password, email=email)
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


# --- New Page Rendering Views ---

def signup_page(request):
    return render(request, 'signup.html')

def login_page(request):
    return render(request, 'login.html')