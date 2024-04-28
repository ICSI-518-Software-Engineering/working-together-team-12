from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

class tickets(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    cinema_id = models.IntegerField()
    film_id = models.IntegerField()
    date = models.CharField(max_length=20)
    showtime=models.CharField(max_length=10)
    seat_no = models.CharField(max_length=10)

    def __str__(self):
        return f"Booking {self.pk} by {self.user.username}"