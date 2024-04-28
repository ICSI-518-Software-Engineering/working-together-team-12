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

def save_card(user_instance, card_number, cvv, expiry_month, expiry_year, card_holder_name, ):
    PaymentDetail.objects.create(
        user_profile=user_instance,
        card_number=int(card_number),
        cvv=int(cvv),
        expiry_year=int(expiry_year),
        expiry_month=int(expiry_month),
        card_holder_name=card_holder_name,
    )


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
