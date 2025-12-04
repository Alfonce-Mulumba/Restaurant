from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    people = models.IntegerField()
    date = models.DateField()
    time = models.TimeField()
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.date} {self.time}"

class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    is_occupied = models.BooleanField(default=False)
    image = models.ImageField(upload_to='rooms/')
    capacity = models.PositiveIntegerField()
    price = models.PositiveIntegerField(help_text="Price in KES")
    description = models.TextField(help_text="E.g., Wifi, AC, Swimming Pool, etc.")
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.room_number}"

class RoomBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    age = models.PositiveIntegerField()
    id_number = models.CharField(max_length=50)
    people = models.PositiveIntegerField()
    check_in = models.DateField()
    check_out = models.DateField()
    message = models.TextField(blank=True, null=True)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - Room {self.room.room_number}"

    def save(self, *args, **kwargs):
        # Ensure check_in/check_out are date objects
        if isinstance(self.check_in, str):
            self.check_in = datetime.strptime(self.check_in, "%Y-%m-%d").date()
        if isinstance(self.check_out, str):
            self.check_out = datetime.strptime(self.check_out, "%Y-%m-%d").date()

        # Example validation
        today = timezone.now().date()
        if not (self.check_in <= today <= self.check_out):
            # optional: raise error or skip
            pass

        super().save(*args, **kwargs)