from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name= models.CharField(max_length=100)
    # bio = models.TextField(null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    address = models.TextField(null=True,blank=True)
    phno = models.IntegerField(null=True, blank=True)

class PaymentDetail(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='payment_details')
    card_number = models.CharField(max_length=16)
    cvv = models.CharField(max_length=4)  
    card_holder_name = models.CharField(max_length=100, default='')
    expiry_date = models.DateField()

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
    created =models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Visit to {self.city_name} on {self.visit_date}"
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