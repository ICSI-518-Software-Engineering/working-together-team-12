from django.shortcuts import render, redirect,get_object_or_404
from django.http import Http404
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import AirportLOCID, City, HotelBooking, HotelCustomer, RestrauntBooking, RestrauntCustomer
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
import random
import time
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.timezone import now


from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm, UserProfileForm,PaymentDetailForm
from django.contrib.auth.decorators import login_required
from .models import UserProfile,PaymentDetail,CitySelection
from django.contrib import messages
import requests
from django.urls import reverse
import datetime 
from .models import MovieTickets, OTPStorage
import json
from .models import FlightBooking, Passenger
import time

@csrf_exempt
def register(request):
    if request.method == 'POST':
        error_messages = []
        username = request.POST['username']
        email = request.POST['email'].rstrip()
        # print(request.POST)
        if User.objects.filter(username=username).exists():
            error_messages.append('Username already taken.')
        if User.objects.filter(email=email).exists():
            error_messages.append('Email already in use.')
        form = UserRegisterForm(request.POST)
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if len(error_messages)==0:
            user = User.objects.create_user(username=username, email=email, password=password1)
            context = {'username': username}
            subject = 'Welcome to BookNow Site!'
            html_message = render_to_string('welcome_email.html', context)
            plain_message = strip_tags(html_message) 
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            # message = f'''Hi {username},\n\nWelcome to OneStopApp Site! We are excited to have you on board.\n\nYour account has been successfully created. Start exploring our platform to discover amazing movies, book tickets, find great hotels and restaurants, and plan your next adventure!\n\nFeel free to reach out to us if you have any questions or need assistance.\n\nBest regards,\nOneStopBooking Team'''            
            # email_from = settings.EMAIL_HOST_USER
            # recipient_list = [email]
            # print(email)
            # send_mail(subject, message, email_from, recipient_list)
            send_mail(subject, plain_message, email_from, recipient_list, html_message=html_message)

            return JsonResponse({'success': True, 'redirect_url': reverse('login') })
        else:
            return JsonResponse({'success': False,'errors':error_messages[0]})

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
            return redirect(home)
        else:
            return render(request, 'login.html', {"message": "Invalid Username or Password"})
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

def forgot_password(request):
    print("forgot_pass")
    if request.method == 'GET':
        return render(request, 'forgot_password.html', {'show_form':True, 'show_error': False})
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            subject = "Password Reset"
            otp = ''.join(random.sample(str(int(time.time())), 5))
            context = {
                'otp': otp
            }
            html_message = render_to_string('reset_password_email.html', context)
            plain_message = strip_tags(html_message)  

            from_email = settings.EMAIL_HOST_USER
            to_email = [email]

            send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
            #
            OTPStorage.objects.create(email=email, otp=otp)
            #
            response =  redirect(reset_password)
            response.set_cookie('email', email, max_age=3600)  # expires in 1 hour
            return response

        else:
            return render(request, 'forgot_password.html', {'show_form': True,'show_error': True})


def reset_password(request):
    if request.method == 'GET':
        return render(request, 'reset_password.html', {'show_otp_form':True})
    if request.method == 'POST':
        email = request.COOKIES.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        otp = request.POST.get('otp')
        time_limit = now() - datetime.timedelta(minutes=5)
        if otp :
            try:
                entry = OTPStorage.objects.get(email=email, otp=otp, created_date__gte=time_limit)
                entry.delete()
                return render(request, 'reset_password.html', {'show_otp_form':False})
            except:
                return render(request, 'reset_password.html', {'show_otp_form':True, "show_otp_error":True})
        else:
            if password and confirm_password: 
                #compare with old password
                user = authenticate(request, email=email, password=password)
                if (password == confirm_password) and (not user):
                    user = User.objects.get(email=email )
                    print("changing password to", password)
                    user.set_password(password)
                    user.save()
                    return redirect(user_login)
                else:
                    return render(request, 'reset_password.html', {'show_otp_form':False, 'show_password_error': True})
            else:
                return render(request, 'reset_password.html', {'show_otp_form':False, 'show_password_error': True})

        
            

@csrf_exempt
def profile(request):
    print(f"invoked by ",request.user.username)
    UserProfile.objects.get_or_create(user=request.user) 
    user_profile = request.user.userprofile
    payment_details = user_profile.payment_details.all()  
    print(payment_details)
    profile_form = UserProfileForm(instance=user_profile)
    payment_form = PaymentDetailForm()
    # print(user_profile)

    
    form_type = request.POST.get('type')
    if request.method == 'POST':

        # print('post method in profile')
        print(request.POST)
        if form_type == 'profileForm':  
            first_name = request.POST.get('firstName')
            last_name = request.POST.get('lastName')
            email = request.POST.get('email')
            # flat_details = request.POST.get('flatDetails')
            # line1 = request.POST.get('line1')
            # line2 = request.POST.get('line2')
            # state = request.POST.get('state')
            country = request.POST.get('country')
            country_code = request.POST.get('countryCode')
            phno = request.POST.get('phno')
            profile_pic = request.FILES.get('profileImage')
            matching_profiles = UserProfile.objects.filter(email=email)

            if len(matching_profiles)>1:
                return JsonResponse({'success': False, 'error':'email already exists'})
            if len(matching_profiles)>=1 and matching_profiles[0].user!=request.user:
                return JsonResponse({'success': False, 'error':'email already exists'})

            
            user_instance = request.user
            defaults={
                    'name': first_name,
                    'lname':last_name,
                    'email': email,
                    # 'address': flat_details,
                    # 'line1': line1,
                    # 'line2': line2,
                    # 'state': state,
                    'country': country,
                    'country_code': int(country_code),
                    'phno': int(phno),
                }
            if profile_pic!= '': 
                defaults['profile_pic'] = profile_pic
            user_profile, created = UserProfile.objects.update_or_create(
                user=user_instance,
                defaults=defaults
            )

            print('created',created)
            print(user_profile)
            return JsonResponse({'success': True, 'redirect_url': reverse('profile') })

        elif form_type == 'AddressForm':
            flat_details = request.POST.get('flatDetails')
            line1 = request.POST.get('line1')
            line2 = request.POST.get('line2')
            state = request.POST.get('state')

            user_instance = request.user
            defaults={
                    'address': flat_details,
                    'line1': line1,
                    'line2': line2,
                    'state': state,
                }
            user_profile, created = UserProfile.objects.update_or_create(
                user=user_instance,
                defaults=defaults
            )

            print('created',created)
            print(user_profile)
            return JsonResponse({'success': True, 'redirect_url': reverse('profile') })

        elif form_type == 'paymentForm':
            print(request.POST) 
            user_instance = get_object_or_404(UserProfile, user=request.user)
            card_number = request.POST.get('card_number')
            cvv = request.POST.get('cvv')
            expiry_month = request.POST.get('expiry_month')
            expiry_year = request.POST.get('expiry_year')
            card_holder_name = request.POST.get('card_holder_name')
            PaymentDetail.objects.create(
                user_profile=user_instance,
                card_number=int(card_number),
                cvv=int(cvv),
                expiry_year=int(expiry_year),
                expiry_month=int(expiry_month),
                card_holder_name=card_holder_name,
            )
            return JsonResponse({'success': True, 'redirect_url': reverse('profile') })
            
    bookings = MovieTickets.objects.filter(user=request.user,payment=True).order_by('-showtime')

    flight_bookings = FlightBooking.objects.filter(user=request.user)
    flight_bookings_filtered = []
    for booking in flight_bookings:
        data = []
        data.extend([booking.booking_id, booking.arrival_airport, booking.departure_airport,  booking.duration, booking.price])
        # passengers = Passenger.objects.filter(booking=booking)
        # for passenger in passengers:
        #     data.extend(passenger.first_name,passenger.last_name,passenger.age,passenger.dl_number)
        flight_bookings_filtered.append(data)

    hotel_bookings = HotelBooking.objects.filter(user=request.user)
    hotel_bookings_filtered = []

    for booking in hotel_bookings:
        data = []
        data.extend([booking.booking_id, booking.hotel_name, booking.checkin_date, booking.checkout_date, booking.duration, booking.price])
        # passengers = HotelCustomer.objects.filter(booking=booking)
        # for passenger in passengers:
        #     data.append([passenger.first_name,passenger.last_name,passenger.age,passenger.dl_number])
        hotel_bookings_filtered.append(data)

    restraunt_bookings = RestrauntBooking.objects.filter(user=request.user)
    restraunt_bookings_filtered = []

    for booking in restraunt_bookings:
        data = []
        data.extend([booking.booking_id, booking.restraunt_name, booking.visit_date])
        # passengers = RestrauntCustomer.objects.filter(booking=booking)
        # for passenger in passengers:
        #     data.extend([passenger.first_name,passenger.last_name,passenger.age,passenger.dl_number])
        restraunt_bookings_filtered.append(data)
    # print(user_profile.profile_pic.url)
    context = {
        'user_profile': user_profile,
        'payment_form': payment_form,
        'payment_details': payment_details,
        'bookings': bookings,
        'flight_bookings': flight_bookings_filtered,
        'hotel_bookings': hotel_bookings_filtered,
        'restraunt_bookings': restraunt_bookings_filtered
    }
    return render(request, 'profile.html', context)

@login_required
def history(request):

    bookings = MovieTickets.objects.filter(user=request.user,payment=True).order_by('-showtime')
    flight_bookings = FlightBooking.objects.filter(user=request.user)
    flight_bookings_filtered = []
    for booking in flight_bookings:
        data = []
        data.extend([booking.booking_id, booking.arrival_airport, booking.departure_airport,  booking.duration, booking.price])
        passengers = Passenger.objects.filter(booking=booking)
        # for passenger in passengers:
        #     data.extend(passenger.first_name,passenger.last_name,passenger.age,passenger.dl_number)
        flight_bookings_filtered.append(data)

    hotel_bookings = HotelBooking.objects.filter(user=request.user)
    hotel_bookings_filtered = []

    for booking in hotel_bookings:
        data = []
        data.extend([booking.booking_id, booking.hotel_name, booking.checkin_date, booking.checkout_date, booking.duration, booking.price])
        passengers = HotelCustomer.objects.filter(booking=booking)
        # for passenger in passengers:
        #     data.append([passenger.first_name,passenger.last_name,passenger.age,passenger.dl_number])
        hotel_bookings_filtered.append(data)

    restraunt_bookings = RestrauntBooking.objects.filter(user=request.user)
    restraunt_bookings_filtered = []

    for booking in restraunt_bookings:
        data = []
        data.extend([booking.booking_id, booking.restraunt_name, booking.visit_date])
        passengers = RestrauntCustomer.objects.filter(booking=booking)
        # for passenger in passengers:
        #     data.extend([passenger.first_name,passenger.last_name,passenger.age,passenger.dl_number])
        restraunt_bookings_filtered.append(data)

    context = {
        'bookings': bookings,
        'flight_bookings': flight_bookings_filtered,
        'hotel_bookings': hotel_bookings_filtered,
        'restraunt_bookings': restraunt_bookings_filtered
    }

    return render(request, 'history.html', context)

@login_required
def home(request):
    return render(request, 'startingpage.html')


def select_seats(request, movie_name, theater_name, showtime):
    tickets = MovieTickets.objects.filter(
        movie=movie_name, 
        theater=theater_name,
        showtime=showtime,
        payment=True
    )
    booked_seats = []
    for ticket in tickets:
        booked_seats.extend(ticket.tickets.split(','))

    booked_seats = [seat.strip() for seat in booked_seats]
    context = {
        'movie_name': movie_name,
        'theatre_name': theater_name,
        'showtime': showtime,
        'booked_seats': booked_seats,
    }
    print(booked_seats)
    return render(request, 'seat.html', context)
@csrf_exempt
def booking_view(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        print(body_data)
        showtime = body_data.get('showtime', '')
        date = body_data.get('date', '')
        seats = body_data.get('seats', '')
        movie_name=body_data.get('movieName', '')
        theatre_name=body_data.get('theaterName', '')

        created = MovieTickets.objects.create(
            user=request.user,
            movie=movie_name.strip(),
            theater=theatre_name.strip(),
            showtime=showtime.strip(),
            tickets= seats.strip()  
        )    
        print(f"/paymentportal/{movie_name}/booking_id/{created.booking_id}/theatre/{theatre_name}/showtime/{showtime}/ticket_count/{len(seats.split(','))}")
        # return JsonResponse({'success': True, 'redirect_url': f"/paymentportal/{movie_name}/booking_id/{created.booking_id}/theatre/{theatre_name}/showtime/{showtime}/ticket_count/{len(seats.split(','))}"})
        return JsonResponse({'success': True, 'redirect_url': f"/paymentportal/{created.booking_id}"})


    return JsonResponse({'error': 'Invalid request'}, status=400)
def movies_home(request):
    latest_selection = CitySelection.objects.filter(user=request.user).order_by('-created').first()
    print('latest_selection in movies',latest_selection)
    data={}
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
                'latitude': '42.6664"',
                'longitude': '-73.7987'
            }  
    else:
         data = {
                        'city_name': 'Albany',
                        'state_name': 'New York',
                        'latitude': '42.6664"',
                        'longitude': '-73.7987'
                    }                 
    print(data)
    theaters_url = "https://flixster.p.rapidapi.com/theaters/list"  

    theaters_query = {"latitude":data['latitude'],"longitude":data['longitude'], "radius": "50"}
    print('theaters_query',theaters_query)
    theaters_headers = {
        'X-RapidAPI-Key': 'ee92e90528msh5c7ce596da5ee43p16c4fajsn512eea1cd54d',  
        "X-RapidAPI-Host": "flixster.p.rapidapi.com"
    }
    theaters_response = requests.get(theaters_url, headers=theaters_headers, params=theaters_query)
    print(theaters_response,'theaters_response')
    theaters_data = theaters_response.json()['data']['theaters'][:2] 
    movies_dict = {}


    for theater in theaters_data:
        if theater.get('hasShowtimes') == "true":
            detail_url = "https://flixster.p.rapidapi.com/theaters/detail"
            detail_query = {"id": theater.get('id')}
            print(theater.get('id'))
            detail_response = requests.get(detail_url, headers=theaters_headers, params=detail_query)
            detail_data = detail_response.json()

            movies = detail_data.get('data', {}).get('theaterShowtimeGroupings', {}).get('movies', [])
            for movie in movies:
                # print("movie",movie)
                emsVersionId = movie.get('emsVersionId')
                if emsVersionId:  
                    if emsVersionId not in movies_dict:
                        if movie.get('posterImage', {}):
                            if movie.get('tomatoRating') and 'tomatometer' in movie['tomatoRating']:
                                rating = movie['tomatoRating']['tomatometer']
                            else:
                                rating = random.randint(50, 95)
                            movies_dict[emsVersionId] = {
                                'name': movie.get('name'),
                                'image_url': movie.get('posterImage', {}).get('url'),
                                'rating': rating,
                                'theaters': {}
                            }
                    
                    showtimes = []
                    for variant in movie.get('movieVariants', []):
                        for group in variant.get('amenityGroups', []):
                            for showtime in group.get('showtimes', []):
                                showtimes.extend([showtime['sdate']])

                    showtimes = list(set(showtimes))
                    if movie.get('posterImage', {}):
                    
                        movies_dict[emsVersionId]['theaters'][theater.get('id')] = {
                            'name': theater.get('name'),
                            'showtimes': showtimes,
                            'emsVersionId':emsVersionId
                        }

    # print(movies_dict)
    for movie_id, movie in movies_dict.items():
        for theater_id, theater_info in movie['theaters'].items():
            formatted_showtimes = []
            for showtime in theater_info['showtimes']:
                # Split the showtime string and keep only the time part
                formatted_showtimes.append(showtime.split('+')[1] if '+' in showtime else showtime)
            theater_info['showtimes'] = formatted_showtimes
    request.session['movies_dict'] = movies_dict
    return render(request, 'movies_home.html', {'movies_dict': movies_dict,'city_name':f"{data['city_name']}, {data['state_name']}"})

def movie_detail(request, emsVersionId):
    movies_dict = request.session.get('movies_dict', {})
    url = "https://flixster.p.rapidapi.com/movies/detail"

    querystring = {"emsVersionId": emsVersionId}

    headers = {
        'X-RapidAPI-Key': '574f37c05cmsh2da5a8f03a076f5p175efajsn5cb41d217d2d',
        'X-RapidAPI-Host': 'flixster.p.rapidapi.com'
    }
    response = requests.get(url, headers=headers, params=querystring)
    mvin = response.json().get('data', {}).get('movie', {})
    genres = mvin.get('genres', [])
    genre_names = [genre.get('name', 'No genre') for genre in genres] if genres else ['No genre available']

    poster_image_dict = mvin.get('posterImage', {})
    poster_image_url = poster_image_dict.get('url', 'No image available') if poster_image_dict else 'No image available'

    tomato_rating_dict = mvin.get('tomatoRating', {})
    tomatometer_rating = tomato_rating_dict.get('tomatometer', 'No rating available') if tomato_rating_dict else 'No rating available'

    # Extract additional movie information
    synopsis = mvin.get('synopsis', 'No description available')
    cast = mvin.get('cast', [])
    directed_by = mvin.get('directedBy', 'Director information not available')
    duration_minutes = mvin.get('durationMinutes', 'Duration information not available')
    release_date = mvin.get('releaseDate', 'Release date not available')
    availability_window = mvin.get('availabilityWindow', 'Availability window not available')
    total_gross = mvin.get('totalGross', 'Total gross not available')

    # Extract basic movie information
    movie_data = {
        'title': mvin.get('name', 'No title available'),
        'release_date': release_date,
        'genres': genre_names,
        'poster_image_url': poster_image_url,
        'tomatometer_rating': tomatometer_rating,
        'synopsis': synopsis,
        'cast': cast,
        'directed_by': directed_by,
        'duration_minutes': duration_minutes,
        'availability_window': availability_window,
        'total_gross': total_gross
    }

    # Store the movie data in the movies_dict object
    movies_dict['movie_id'] = movie_data


    movie = movies_dict.get(emsVersionId)
    # print(movie)
    if not movie:
        return redirect('movies_home')  

    return render(request, 'movie_detail.html', {'movie': movie,'movie_data':movie_data})
def showtime_detail(request, emsVersionId, theaterId, showtime):
    context = {
        'emsVersionId': emsVersionId,
        'theaterId': theaterId,
        'showtime': showtime,
    }
    return render(request, 'showtime_detail.html', context)

def hotel_list(request):
    latest_selection = CitySelection.objects.filter(user=request.user).order_by('-created').first()
    print('latest_selection in hotels',latest_selection)
    data={}
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
    else:
         data = {
                        'city_name': 'Albany',
                        'state_name': 'New York',
                        'latitude': '42.6850',
                        'longitude': '73.8248'
                    } 
    print(data)
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
        'X-RapidAPI-Key': '574f37c05cmsh2da5a8f03a076f5p175efajsn5cb41d217d2d',
        'X-RapidAPI-Host': 'local-business-data.p.rapidapi.com'
    }

    response = requests.get(url, headers=headers, params=querystring)
    print(response)
    hotels = response.json().get('data', [])  
    # print(hotels[0])
    # print(hotels)
    request.session['hotels'] = hotels
    return render(request, 'hotels_home.html', {'hotels': hotels,'city_name':f"{data['city_name']}, {data['state_name']}"})

def hotel_detail(request, business_id):
    hotels = request.session.get('hotels', [])
    hotel = next((item for item in hotels if item['business_id'] == business_id), None)
    if hotel is None:
        raise Http404("Hotel does not exist")
    print({'hotel': hotel, "business_id": business_id})
    return render(request, 'hotel_detail.html', {'hotel': hotel, "business_id": business_id})

def book_hotel(request, business_id):

    hotels = request.session.get('hotels', [])
    payment_options = PaymentDetail.objects.filter(user_profile__user=request.user)
    hotel = next((item for item in hotels if item['business_id'] == business_id), None)
    return render(request, 'occupants_details.html', {'hotel': hotel, "business_id": business_id, 'payment_options': payment_options})

def confirm_hotel_booking(request):
    if request.method == 'POST':
        customers = []
        i = 0
        while True:
            fname = request.POST.get(f'fname_{i}')
            lname = request.POST.get(f'lname_{i}')
            age = request.POST.get(f'age_{i}')
            dl_number = request.POST.get(f'dl_number_{i}')
            if not fname:
                break
            customers.append({
                'first_name': fname,
                'last_name': lname,
                'age': age,
                'dl_number': dl_number
            })
            i += 1
        booking_id = int(time.time())
        context = {
            'hotel_name': request.POST.get('hotel_name'),
            'full_address': request.POST.get('full_address'),
            'phone_number': request.POST.get('phone_number'),
            'from_date': request.POST.get('from_date'),
            'to_date': request.POST.get('to_date'),
            'booking_id': booking_id,
            'customers': customers,
            'card_ending': request.POST.get('payment_method'),
            'totalprice': request.POST.get('totalcost'),
        }

        hotel_booking = HotelBooking(
            user = request.user,
            booking_id = booking_id,
            hotel_name = request.POST.get('hotel_name'),
            business_id=booking_id,
            checkin_date=request.POST.get('from_date'),
            checkout_date=request.POST.get('to_date'),
            duration= request.POST.get('totaldays'),
            payment_card_ending=request.POST.get('payment_method'),  # Assuming you want the last 4 digits only
            price=request.POST.get('totalcost'),  # Convert price to float
        )
        hotel_booking.save()

        for passenger in customers:  # Assuming 'passengers' is a list of dictionaries
            HotelCustomer(
                booking=hotel_booking,
                first_name=passenger['first_name'],
                last_name=passenger['last_name'],
                age=int(passenger['age']),
                dl_number=passenger['dl_number']
            ).save()

        subject = "Hotel Booking Confirmation"
        html_message = render_to_string('hotel_booking_confirmation_email.html', context)
        plain_message = strip_tags(html_message)  

        from_email = settings.EMAIL_HOST_USER
        to_email = [request.user.email]
        print("sending mail")
        print(customers)
        send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
        return redirect("home")

def restraunt_list(request):
    latest_selection = CitySelection.objects.filter(user=request.user).order_by('-created').first()
    print('latest_selection',latest_selection)
    print(CitySelection.objects.filter(user=request.user).order_by('-created'))
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
    else:
         data = {
                        'city_name': 'Albany',
                        'state_name': 'New York',
                        'latitude': '42.6850',
                        'longitude': '73.8248'
                    } 

    url = "https://local-business-data.p.rapidapi.com/search"
    querystring = {
        "query": f"Restraunts near {data['city_name']}, {data['state_name']}",
        "limit": "10",
        "lat": data['latitude'],
        "lng": data['longitude'],
        "zoom": "13",
        "language": "en",
        "region": "us"
    }
    print(querystring)
    headers = {
        'X-RapidAPI-Key': '574f37c05cmsh2da5a8f03a076f5p175efajsn5cb41d217d2d',
        'X-RapidAPI-Host': 'local-business-data.p.rapidapi.com'
    }

    response = requests.get(url, headers=headers, params=querystring)
    restraunts = response.json().get('data', [])  
    # print(hotels)
    request.session['restraunts'] = restraunts

    return render(request, 'restraunts_home.html', {'restraunts': restraunts,'city_name':f"{data['city_name']}, {data['state_name']}"})
def restraunt_detail(request, business_id):
    restraunts = request.session.get('restraunts', [])
    restraunt = next((item for item in restraunts if item['business_id'] == business_id), None)
    if restraunt is None:
        raise Http404("restraunt does not exist")

    # print({'restraunt': restraunt, 'business_id': business_id})
    return render(request, 'restraunt_detail.html', {'restraunt': restraunt, 'business_id': business_id})


def book_restraunt(request, business_id):
    restraunts = request.session.get('restraunts', [])
    payment_options = PaymentDetail.objects.filter(user_profile__user=request.user)
    restraunt = next((item for item in restraunts if item['business_id'] == business_id), None)
    return render(request, 'restraunt_occupants_details.html', {'restraunt': restraunt, "business_id": business_id, 'payment_options': payment_options})

def confirm_restraunt_booking(request):
    if request.method == 'POST':
        customers = []
        i = 0
        while True:
            fname = request.POST.get(f'fname_{i}')
            lname = request.POST.get(f'lname_{i}')
            age = request.POST.get(f'age_{i}')
            dl_number = request.POST.get(f'dl_number_{i}')
            if not fname:
                break
            customers.append({
                'first_name': fname,
                'last_name': lname,
                'age': age,
                'dl_number': dl_number
            })
            i += 1
        booking_id = int(time.time())
        context = {
            'restraunt_name': request.POST.get('restraunt_name'),
            'full_address': request.POST.get('full_address'),
            'phone_number': request.POST.get('phone_number'),
            'booking_date': request.POST.get('visit_date'),
            'booking_id': booking_id,
            'customers': customers,
            'card_ending': request.POST.get('payment_method'),
        }

        print("save payment",request.POST.get("save_for_future"))
        print("c no",request.POST.get("card_number"))
        print("c holder name",request.POST.get("card_holder_name"))
        print("expiry date",request.POST.get("expiry_date"))
        print("cvv",request.POST.get("cvv"))

        ## save here

        restraunt_booking = RestrauntBooking(
            user = request.user,
            booking_id = booking_id,
            restraunt_name = request.POST.get('restraunt_name'),
            business_id=booking_id,
            visit_date=request.POST.get('visit_date'),
            payment_card_ending=request.POST.get('payment_method'),  # Assuming you want the last 4 digits only
        )
        restraunt_booking.save()

        for passenger in customers:  # Assuming 'passengers' is a list of dictionaries
            RestrauntCustomer(
                booking=restraunt_booking,
                first_name=passenger['first_name'],
                last_name=passenger['last_name'],
                age=int(passenger['age']),
                dl_number=passenger['dl_number']
            ).save()

        subject = "Restraunt Booking Confirmation"
        html_message = render_to_string('restraunt_booking_confirmation_email.html', context)
        plain_message = strip_tags(html_message)  

        from_email = settings.EMAIL_HOST_USER
        to_email = [request.user.email]
        print("sending mail")
        print(customers)
        send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
        return redirect("home")


def search_flights(request):
    if request.method == 'POST':
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
        departure_date = request.POST.get('departure_date')
        sort_order = request.POST.get('sort_order')
        class_type = request.POST.get('class_type')
        print("origin is", origin)
        print("destination is", destination)
        headers = {
            "X-RapidAPI-Key": "7dbc098597msh8dfc40d52e8a0fcp173ffejsneb6d1efbdb5d",
            "X-RapidAPI-Host": "priceline-com-provider.p.rapidapi.com"
        }
        origin_response = requests.get(
            "https://priceline-com-provider.p.rapidapi.com/v1/flights/locations",
            headers=headers, params={"name": origin}
        )
        print('origin',origin_response.json()[0]['id'])
        destination_response = requests.get(
            "https://priceline-com-provider.p.rapidapi.com/v1/flights/locations",
            headers=headers, params={"name": destination}
        )
        print('origin',destination_response.json()[0]['id'])
        
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

def flight_confirmation(request):
    if request.method == 'POST':
        flight_data = {}
        flight_data["depart_time"] = request.POST.get("depart_time")
        flight_data["arrival_airport"] = request.POST.get("arrival_airport")
        flight_data["depart_airport"] = request.POST.get("depart_airport")
        flight_data["arrival_time"] = request.POST.get("arrival_time")
        flight_data["duration"] = request.POST.get("duration")
        flight_data["price"] = request.POST.get("price")
        
        payment_options = PaymentDetail.objects.filter(user_profile__user=request.user)

        context = {'flight_data': flight_data, 'payment_options': payment_options}
        return render(request, "passenger_details.html", context)

def add_passengers(request):
    if request.method == 'POST':
        passengers = []
        i = 0
        while True:
            fname = request.POST.get(f'fname_{i}')
            lname = request.POST.get(f'lname_{i}')
            age = request.POST.get(f'age_{i}')
            dl_number = request.POST.get(f'dl_number_{i}')
            if not fname:
                break
            passengers.append({
                'first_name': fname,
                'last_name': lname,
                'age': age,
                'dl_number': dl_number
            })
            i += 1

        subject = "Flight Booking Confirmation"
        print(request.POST.get('totalprice'))
        booking_id = str(int(time.time()))
        context = {
        'depart_time': request.POST.get('depart_time'),
        'arrival_airport': request.POST.get('arrival_airport'),
        'depart_airport': request.POST.get('depart_airport'),
        'arrival_time': request.POST.get('arrival_time'),
        'duration': request.POST.get('duration'),
        'booking_id': booking_id,
        'passengers': passengers,
        'card_ending': request.POST.get('payment_method'),
        'totalprice': request.POST.get('totalprice'),
        }
        print("user is", request.user)
        booking = FlightBooking(
            user = request.user,
            # depart_time=request.POST.get('depart_time'),
            arrival_airport=request.POST.get('arrival_airport'),
            departure_airport=request.POST.get('depart_airport'),
            arrival_time=request.POST.get('arrival_time'),
            duration=request.POST.get('duration'),
            booking_id=booking_id,  # Booking ID generated from current time
            payment_card_ending=request.POST.get('payment_method'),  # Assuming you want the last 4 digits only
            price=float(request.POST.get('totalprice')),  # Convert price to float
            thank_you_note="Thank you for your booking!"
        )
        booking.save()

        for passenger in passengers:  # Assuming 'passengers' is a list of dictionaries
            Passenger(
                booking=booking,
                first_name=passenger['first_name'],
                last_name=passenger['last_name'],
                age=int(passenger['age']),
                dl_number=passenger['dl_number']
            ).save()

        html_message = render_to_string('flight_booking_confirmation_email.html', context)
        plain_message = strip_tags(html_message)  

        from_email = settings.EMAIL_HOST_USER
        to_email = [request.user.email]
        print("sending mail")
        send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
        return redirect("home")

    return render(request, 'passenger_details.html')


def flight_results(request, origin_id, destination_id, date, sort_order,class_type):
    headers = {
        "X-RapidAPI-Key": "7dbc098597msh8dfc40d52e8a0fcp173ffejsneb6d1efbdb5d",
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
            # print('before',flight['depart_time'])
            # print('after',flight['depart_time'][11:16])
            flight['formatted_depart_time']=flight['depart_time'][11:16] 
            flight['formatted_arrival_time']=flight['arrival_time'][11:16]  
        # print("flight_data",flight_data)

        # filtered_flights = [
        #     flight for flight in flight_data
        #     if flight['depart_code'] == destination_id and flight['arrival_code'] == origin_id
        # ]
        filtered_flights=flight_data

        # print(filtered_flights)
        return render(request, 'flight_results.html', {'flights': filtered_flights})
    else:
        error_message = "There was a problem retrieving flight data. Please try again."
        return render(request, 'flight_results.html', {'error_message': error_message})
def search_cities(request):
    if 'term' in request.GET:
        qs = City.objects.filter(city_name__icontains=request.GET.get('term'))[:5]
        cities = list(qs.values('city_name', 'state_name', 'lat', 'lng'))
        return JsonResponse(cities, safe=False)
    return JsonResponse([])

def search_airports(request):
    if 'term' in request.GET:
        qs = AirportLOCID.objects.filter(locid__icontains=request.GET.get('term'))[:5]
        airports = list(qs.values('locid',))
        return JsonResponse(airports, safe=False)
    return JsonResponse([])

@csrf_exempt
def save_selection(request):
    if request.method == 'POST':
        city_name = request.POST.get('city_name')
        print('city_name form save_selection',city_name)
        
        visit_date = datetime.datetime.strptime(request.POST.get('visit_date'), '%Y-%m-%d').date()
        # print(city_name,visit_date)
        CitySelection.objects.create(user=request.user,city_name=city_name, visit_date=visit_date)
        redirect_url = reverse('movies_home') 
        latest_selection = CitySelection.objects.filter(user=request.user).order_by('-created').first()
        print('lastest form save_selection',latest_selection)
        time.sleep(2)
        return JsonResponse({'status': 'success', 'redirect_url': redirect_url})
    return JsonResponse({'status': 'failed'}, status=400)

def payment_portal(request, booking_id):
    ticket = get_object_or_404(MovieTickets, pk=booking_id)
    number_of_tickets = len(ticket.tickets.split(',')) 
    total_price = number_of_tickets * 10
    
    # payment_options = PaymentDetail.objects.filter(user_profile__user=request.user)
    
    context = {
        'ticket': ticket,
        'number_of_tickets': number_of_tickets,
        'total_price': total_price,
        # 'payment_options': payment_options,
    }
    
    return render(request, 'payment_portal.html', context)
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
    # payment_method = get_object_or_404(PaymentDetail, id=payment_id, user_profile__user=request.user)
    # card_ending = payment_method.card_number[-4:]
    subject = 'Your Booking Details from BookNow'

    print(str(ticket))
   
    context = {
    'booking_id': booking_id,
    'movie': ticket.movie,
    'theater': ticket.theater,
    'showtime': ticket.showtime,
    'ticket': ticket.tickets,
    'card_ending': "1234",
    'price': price,
    }
    html_message = render_to_string('booking_confirmation_email.html', context)
    plain_message = strip_tags(html_message)  

    from_email = settings.EMAIL_HOST_USER
    to_email = [request.user.email]
    print("sending mail")
    send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
    context = {
        'ticket': ticket,
        'booking_id': booking_id,
        'payment_method':{},
        'price':price
    }
    return render(request, 'show_tickets.html', context)

def delete_payment_info(request):
    payment_detail_card_number = request.POST.get('payment_detail_card_number')
    try:
        payment_detail = PaymentDetail.objects.get(card_number=payment_detail_card_number, user_profile__user=request.user)
        payment_detail.delete()
        messages.success(request, "Payment detail removed successfully.")
    except PaymentDetail.DoesNotExist:
        messages.error(request, "Payment detail not found.")

    return redirect('profile') 