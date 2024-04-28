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

