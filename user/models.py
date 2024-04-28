from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name= models.CharField(max_length=100)
    lname=models.CharField(null=True,max_length=100,blank=True,default='')
    email = models.EmailField(null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    address = models.TextField(null=True,blank=True)
    line1=models.TextField(null=True,blank=True,default='')
    line2=models.TextField(null=True,blank=True,default='')
    state=models.TextField(null=True,blank=True,default='')
    country=models.TextField(null=True,blank=True,default='')
    country_code=models.IntegerField( default=0)
    phno = models.IntegerField( default=0)
    def save(self, *args, **kwargs):
        if not self.email:
            self.email = self.user.email
        super(UserProfile, self).save(*args, **kwargs)

class PaymentDetail(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='payment_details')
    card_number = models.CharField(max_length=16)
    cvv = models.CharField(max_length=4)  
    card_holder_name = models.CharField(max_length=100, default='')
    # expiry_date = models.DateField()
    expiry_month=models.IntegerField(null=True)
    expiry_year=models.IntegerField(null=True)


    def __str__(self):
        return f"{self.user_profile.user.username}'s card ending in {self.card_number[-4:]}"

class City(models.Model):
    city_name = models.CharField(max_length=255)
    state_id = models.CharField(max_length=2)  
    state_name = models.CharField(max_length=100)
    lat = models.FloatField()
    lng = models.FloatField()

    def __str__(self):
        return f"{self.city_name}, {self.state_name} [{self.state_id}]"

class CitySelection(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    city_name = models.CharField(max_length=255)
    visit_date = models.DateField()
    created =models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Visit to {self.city_name} on {self.visit_date} and creted on {self.created}"
class MovieTickets(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    theater = models.CharField(max_length=255)
    movie = models.CharField(max_length=255)
    showtime = models.CharField(max_length=25)
    booking_id = models.AutoField(primary_key=True)
    tickets = models.CharField(max_length=255) 
    payment = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.movie} - {self.showtime} - {self.user} - {self.booking_id}"
    
class OTPStorage(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.otp}"

class AirportLOCID(models.Model):
    # Assuming the CSV has columns for code, name, and location, etc.
    locid = models.CharField(max_length=10, unique=True)
    location = models.CharField(max_length=255)
    
    def __str__(self):
        return self.cid
    
class FlightBooking(models.Model):
    user = models.CharField(max_length=20, default ="123")
    booking_id = models.CharField(max_length=20, unique=True)
    arrival_time = models.TimeField()
    arrival_airport = models.CharField(max_length=100)
    departure_airport = models.CharField(max_length=100)
    duration = models.IntegerField(help_text="Duration in minutes")
    price = models.FloatField()
    payment_card_ending = models.CharField(max_length=4)
    thank_you_note = models.TextField(default="Thank you for your booking!")

    def __str__(self):
        return f"Booking ID {self.booking_id} at {self.arrival_airport}"

class Passenger(models.Model):
    booking = models.ForeignKey(FlightBooking, on_delete=models.CASCADE, related_name="passengers")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    dl_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class HotelBooking(models.Model):
    user = models.CharField(max_length=20, default ="123")
    booking_id = models.CharField(max_length=100, unique=True)
    hotel_name = models.CharField(max_length=100)
    business_id = models.CharField(max_length=100)
    checkin_date = models.DateField()
    checkout_date = models.DateField()
    duration = models.IntegerField(help_text="Duration in days")
    price = models.FloatField()
    payment_card_ending = models.CharField(max_length=4)

    def __str__(self):
        return f"Booking ID {self.booking_id} at {self.arrival_airport}"

class HotelCustomer(models.Model):
    booking = models.ForeignKey(HotelBooking, on_delete=models.CASCADE, related_name="passengers")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    dl_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class RestrauntBooking(models.Model):
    user = models.CharField(max_length=20, default ="123")
    booking_id = models.CharField(max_length=100, unique=True)
    restraunt_name = models.CharField(max_length=100)
    business_id = models.CharField(max_length=100)
    visit_date = models.DateField()
    payment_card_ending = models.CharField(max_length=4)
    def __str__(self):
        return f"Booking ID {self.booking_id} at {self.arrival_airport}"

class RestrauntCustomer(models.Model):
    booking = models.ForeignKey(RestrauntBooking, on_delete=models.CASCADE, related_name="passengers")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    dl_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"