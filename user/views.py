from django.shortcuts import render, redirect,get_object_or_404
from django.http import Http404
from django.http import JsonResponse
from .models import City
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
import random



from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm, UserProfileForm,PaymentDetailForm
from django.contrib.auth.decorators import login_required
from .models import UserProfile,PaymentDetail,CitySelection
from django.contrib import messages
import requests
from django.urls import reverse
from datetime import datetime 
from .models import MovieTickets
import json


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email'].rstrip()
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            subject = 'Welcome to OneStopApp Site!'
            message = f'Hi {username}, your account has been successfully created.'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            print(email)
            send_mail(subject, message, email_from, recipient_list)
            return redirect('login')  
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return render(request, 'startingpage.html')     
    return render(request, 'login.html')
def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user.is_staff:
            login(request, user)
            return render(request, 'AdminPage.html') 
    return render(request, 'admin_login.html')


def user_logout(request):
    logout(request)
    return redirect('login')  

def profile(request):
    UserProfile.objects.get_or_create(user=request.user) 
    user_profile = request.user.userprofile
    payment_details = user_profile.payment_details.all()  

    profile_form = UserProfileForm(instance=user_profile)
    payment_form = PaymentDetailForm()
    form_type = request.POST.get('form_type')
    if request.method == 'POST':
        print('post method in profile')
        if form_type == 'update_profile_form':  
            profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
            print('profile form not valid')
            if profile_form.is_valid():
                profile_form.save()
                print('profile form  valid')

                messages.success(request, 'Your profile has been updated!')
                return redirect('profile')  

        elif 'add_payment' in request.POST: 
            payment_form = PaymentDetailForm(request.POST)
            print("paymet form not valid")
            print(payment_form)
            if payment_form.is_valid():
                print("paymet form valid")
                new_payment_detail = payment_form.save(commit=False)
                new_payment_detail.user_profile = user_profile
                new_payment_detail.save()
                messages.success(request, 'Your payment details have been updated!')
                return redirect('profile') 

   
    context = {
        'profile_form': profile_form,
        'payment_form': payment_form,
        'payment_details': payment_details,
    }
    return render(request, 'profile.html', context)
@login_required
def history(request):
    bookings = MovieTickets.objects.filter(user=request.user,payment=True).order_by('-showtime')
    
    context = {
        'bookings': bookings
    }
    return render(request, 'history.html', context)
@login_required
def home(request):
    return render(request, 'startingpage.html')



def search_cities(request):
    if 'term' in request.GET:
        qs = City.objects.filter(city_name__icontains=request.GET.get('term'))[:5]
        cities = list(qs.values('city_name', 'state_name', 'lat', 'lng'))
        return JsonResponse(cities, safe=False)
    return JsonResponse([])
def save_selection(request):
    if request.method == 'POST':
        city_name = request.POST.get('city_name')
        
        visit_date = datetime.strptime(request.POST.get('visit_date'), '%Y-%m-%d').date()
        print(city_name,visit_date)
        CitySelection.objects.create(user=request.user,city_name=city_name, visit_date=visit_date)
        redirect_url = reverse('movies_home') 
        return JsonResponse({'status': 'success', 'redirect_url': redirect_url})
    return JsonResponse({'status': 'failed'}, status=400)



























































































































































def hotel_list(request):
    latest_selection = CitySelection.objects.filter(user=request.user).order_by('-created').first()
    if latest_selection is not None:
        parts = latest_selection.city_name.split(',')
        if len(parts) >= 2:
            city_name = parts[0].strip()  
            state_name = parts[1].strip() 
        matching_city = City.objects.filter(city_name=city_name, state_name=state_name).first()    
        if matching_city:
                    data = {
                        'city_name': matching_city.city_name,
                        'state_name': matching_city.state_name,
                        'latitude': str(matching_city.lat),
                        'longitude': str(matching_city.lng)
                    }
    else:
         data = {
                        'city_name': 'Albany',
                        'state_name': 'New York',
                        'latitude': '42.6850',
                        'longitude': '73.8248'
                    } 

    url = "https://local-business-data.p.rapidapi.com/search"
    querystring = {
        "query": f"hotels near {data['city_name']}, {data['state_name']}",
        "limit": "10",
        "lat": data['latitude'],
        "lng": data['longitude'],
        "zoom": "13",
        "language": "en",
        "region": "us"
    }
    headers = {
        "X-RapidAPI-Key": "f980ede61dmshd87d831abfdc365p13d4e5jsncfcae06fb6c8",
        "X-RapidAPI-Host": "local-business-data.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    print(response)
    hotels = response.json().get('data', [])  
    print(hotels)
    request.session['hotels'] = hotels
    return render(request, 'hotels_home.html', {'hotels': hotels})
def hotel_detail(request, business_id):
    hotels = request.session.get('hotels', [])
    hotel = next((item for item in hotels if item['business_id'] == business_id), None)
    if hotel is None:
        raise Http404("Hotel does not exist")
    return render(request, 'hotel_detail.html', {'hotel': hotel})




















































def search_flights(request):
    if request.method == 'POST':
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
        departure_date = request.POST.get('departure_date')
        sort_order = request.POST.get('sort_order')
        class_type = request.POST.get('class_type')

        headers = {
            "X-RapidAPI-Key": "f980ede61dmshd87d831abfdc365p13d4e5jsncfcae06fb6c8",
            "X-RapidAPI-Host": "priceline-com-provider.p.rapidapi.com"
        }
        origin_response = requests.get(
            "https://priceline-com-provider.p.rapidapi.com/v1/flights/locations",
            headers=headers, params={"name": origin}
        )
        destination_response = requests.get(
            "https://priceline-com-provider.p.rapidapi.com/v1/flights/locations",
            headers=headers, params={"name": destination}
        )
        
        if origin_response.ok and destination_response.ok:
            origin_id = origin_response.json()[0]['id']
            destination_id = destination_response.json()[0]['id']
            print(origin_id,destination_id)

            # Redirect to the flight results page, passing necessary information
            return redirect('flight_results', origin_id=origin_id, destination_id=destination_id, date=departure_date, sort_order=sort_order,class_type=class_type)
        else:
            error_message = "There was a problem finding the locations. Please try again."
            return render(request, 'search_flights.html', {'error_message': error_message})

    return render(request, 'flights_home.html')

def flight_results(request, origin_id, destination_id, date, sort_order,class_type):
    headers = {
        "X-RapidAPI-Key": "f980ede61dmshd87d831abfdc365p13d4e5jsncfcae06fb6c8",
        "X-RapidAPI-Host": "priceline-com-provider.p.rapidapi.com"
    }
    querystring = {
        "location_arrival": destination_id,
        "date_departure": date,
        "sort_order": sort_order.upper(),  
        "location_departure": origin_id,
        "class_type":class_type.upper(),
        "itinerary_type": "ONE_WAY",  
    }
    print(querystring)
    response = requests.get(
        "https://priceline-com-provider.p.rapidapi.com/v1/flights/search",
        headers=headers, params=querystring
    )
    if response.ok:
        flight_data = []
    if response.ok:
        flights_json = response.json()  
        # print('flight_json',flights_json)
        listings = flights_json.get('data', {}).get('listings', [])
        # print('---------------------------------------')
        # print(listings)
        # print('---------------------------------------')

        for flight in listings:
            if 'airlines' in flight and flight['airlines']:
                # print('---------------------------------------')
                # print(flight)
                # print('---------------------------------------')

                airline=flight.get('airlines',[])[0]
                airline
                flight_details = {
                    'id': flight.get('id'),
                    'price': flight.get('totalPriceWithDecimal', {}).get('price'),
                    'airlines':airline['name'],
                    'segments': []  
                }
                for slice_detail in flight.get('slices', []):
                    for segment in slice_detail.get('segments', []):
                        segment_details = {
                            'depart_airport': segment.get('departInfo', {}).get('airport', {}).get('name'),
                            'depart_code':segment.get('departInfo', {}).get('airport', {}).get('code'),
                            'depart_time': segment.get('departInfo', {}).get('time', {}).get('dateTime'),
                            'arrival_airport': segment.get('arrivalInfo', {}).get('airport', {}).get('name'),
                            'arrival_code': segment.get('arrivalInfo', {}).get('airport', {}).get('code'),
                            'arrival_time': segment.get('arrivalInfo', {}).get('time', {}).get('dateTime'),
                            'duration': segment.get('duration')
                        }
                        flight_details['segments'].append(segment_details)
                        break
                flight_data.append(flight_details)

        for flight in flight_data:
            segment = flight['segments'][0]
            flight.update(segment)  
            del flight['segments']
            print('before',flight['depart_time'])
            print('after',flight['depart_time'][11:16])
            flight['formatted_depart_time']=flight['depart_time'][11:16] 
            flight['formatted_arrival_time']=flight['arrival_time'][11:16]  
        # print("flight_data",flight_data)

        # filtered_flights = [
        #     flight for flight in flight_data
        #     if flight['depart_code'] == destination_id and flight['arrival_code'] == origin_id
        # ]
        filtered_flights=flight_data

        print(filtered_flights)
        return render(request, 'flight_results.html', {'flights': filtered_flights})
    else:
        error_message = "There was a problem retrieving flight data. Please try again."
        return render(request, 'flight_results.html', {'error_message': error_message})















































































































































@csrf_exempt  
def payment_confirmation(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        payment_method_id = request.POST.get('payment_method')
        total_price = request.POST.get('total_price') 
        ticket = get_object_or_404(MovieTickets, pk=booking_id)
        ticket.payment = True
        ticket.save()
        
        redirect_url = f"/show_tickets/{booking_id}/payment/{payment_method_id}/price/{total_price}"
 
        return JsonResponse({'status': 'success','redirect_url': redirect_url})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
def show_tickets(request, booking_id,payment_id,price):

    ticket = get_object_or_404(MovieTickets, booking_id=booking_id, user=request.user)
    payment_method = get_object_or_404(PaymentDetail, id=payment_id, user_profile__user=request.user)
    card_ending = payment_method.card_number[-4:]
    subject = 'Your Booking Details'
    message = f"""
    Booking ID: {booking_id}
    Movie: {ticket.movie}
    Theatre: {ticket.theater}
    Showtime: {ticket.showtime}
    Paid using the card ending with {card_ending}
    Price: ${price}
    """
    from_email = settings.EMAIL_HOST_USER  
    to_email = [request.user.email] 

    send_mail(subject, message, from_email, to_email)
    context = {
        'ticket': ticket,
        'booking_id': booking_id,
        'payment_method':payment_method,
        'price':price
    }

    return render(request, 'show_tickets.html', context)
