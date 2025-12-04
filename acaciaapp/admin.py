from django.contrib import admin
from .models import Room, RoomBooking, Reservation

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'capacity', 'price', 'available')
    list_editable = ('available',)  # only fields that exist in the model

@admin.register(RoomBooking)
class RoomBookingAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'room', 'check_in', 'check_out', 'email', 'phone')
    list_editable = ()  # you can choose fields, but only existing ones

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'people', 'date', 'time', 'user')
