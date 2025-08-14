from django.contrib import admin
from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Page URLs
    path('', views.index_page, name='index'),
    path('destinations/', views.destinations_page, name='destinations'),
    path('accommodation/', views.accommodation_page, name='accommodation'),
    path('travel-agencies/', views.travel_agencies_page, name='travel_agencies'),
    path('car-rentals/', views.car_rentals_page, name='car_rentals'),
    path('profile/', views.profile_page, name='profile'),
    path('trip-summary/', views.trip_summary_page, name='trip_summary'),
    path('trip/view/<int:trip_id>/', views.view_saved_trip_page, name='view_saved_trip'),
    path('terms-conditions/', views.terms_conditions_page, name='terms_conditions'),
    path('privacy-policy/', views.privacy_policy_page, name='privacy_policy'),
    path('signup/', views.signup_page, name='signup'),
    path('login/', views.login_page, name='login'),

    # API URLs
    path('api/destinations/<int:destination_id>/attractions/', views.attraction_list_api, name='attraction-list-api'),
    path('api/accommodations/', views.accommodation_list_api, name='accommodation-list-api'),
    path('api/car-rentals/', views.car_rental_list_api, name='car-rental-list-api'),
    path('api/travel-agencies/', views.travel_agency_list_api, name='travel-agency-list-api'),
    path('api/signup/', views.signup_api, name='signup-api'),
    path('api/login/', views.login_api, name='login-api'),
    path('api/logout/', views.logout_api, name='logout-api'),
    path('api/trip/add/', views.add_to_trip_api, name='add-to-trip-api'),
    path('api/trip/dates/', views.update_trip_dates_api, name='update-trip-dates-api'),
    path('api/trip/save/', views.save_trip_api, name='save-trip-api'),
    path('api/profile/', views.profile_api, name='profile-api'),
    path('api/trip/summary/', views.get_trip_summary_api, name='get-trip-summary-api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)