from django.shortcuts import render, redirect
from accounts.models import *
from django.http import HttpResponseRedirect
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from .models import tickets
# Create your views here.


def index(request):
    return render(request,"index.html")



def show_tickets(request, cinema_id, film_id, showtime,date):
    booked_tickets = tickets.objects.filter(
    cinema_id=cinema_id,
    film_id=film_id,
    date=date,
    showtime=showtime,
    ).values_list('seat_no', flat=True)
    
    booked_seat_list = list(booked_tickets)
    booked_seats_string = ", ".join(booked_seat_list)
    details = {
        'cinema_id': cinema_id,
        'film_id': film_id,
        'showtime': showtime,
        'date': date,
        'booked_seats': booked_seats_string,  
    }

    return render(request,"ticket.html", {'ticket':details})
def movies_landing_page(request):
    return render(request,"movies_landing_page.html")

@csrf_exempt
def post_cinemas_for_film(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        request.session['cinemas_data'] = data  
        return JsonResponse({'success': True, 'redirect_url': 'show_cinemas_for_movie'})

def show_cinemas_for_movie(request):
    cinemas_data = request.session.get('cinemas_data', '{}') 
    # print(cinemas_data)
    return render(request, 'show_cinemas_for_movie.html', {'cinema_data': cinemas_data})

def seat_selection(request,cinema_id, film_id, showtime,date):
    booked_seats = tickets.objects.filter(
        cinema_id=cinema_id,
        film_id=film_id,
        date=date,
        showtime=showtime,
    ).values_list('seat_no', flat=True)
    
    # Convert QuerySet to a list of seat numbers
    booked_seat_list = list(booked_seats)

    details = {
        'cinema_id': cinema_id,
        'film_id': film_id,
        'showtime': showtime,
        'date': date,
        'booked_seats': booked_seat_list,  # Add booked seats to the details
    }
    return render(request, 'seat.html', {'details': details})
@csrf_exempt
@login_required
def booking_view(request,cinema_id, film_id, showtime,date):
    # seat_numbers = request.POST.get('seats')  # Adjust based on actual data sent
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        seats = body_data.get('seats', '').split(', ')
        for seat_no in seats:
            ticket = tickets.objects.create(
                user=request.user,
                cinema_id=cinema_id,
                film_id=film_id,
                date=date,
                showtime=showtime,
                seat_no=seat_no.strip()  # Remove any leading/trailing whitespace
            )

        # print(seats) 

    # print(request.POST)
    # print(seat_numbers)
        return JsonResponse({'success': True,'redirect_url': f'/show_tickets/{cinema_id}/film/{film_id}/showtime/{showtime}/date/{date}/'})
    return JsonResponse({'error': 'Invalid request'}, status=400)
@csrf_exempt
def movie_search(request):
    if request.method=='POST':
        films_data = request.POST.get('films_data')
        print('movie_search data:',films_data)
        request.session['movie_search_data'] = films_data
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def fetch_movies(request):  
    films_data = request.session.get('movie_search_data')
    # print('movie_fetch data:',films_data)
    films_data_parsed = json.loads(films_data)
    context = {'films_data': films_data_parsed}
    return render(request, 'movie_search.html', context)
@csrf_exempt
def load_movie(request):
    if request.method=='POST':
        movie_data = json.loads(request.body)
        print("movie_data:",movie_data)

        request.session['movie_data'] = movie_data
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
def movie_details(request):
    movie_data = request.session.get('movie_data')
    print("movie_data:",movie_data)
    context = {'movie_data': movie_data}
    return render(request, 'movie_details.html', context)
