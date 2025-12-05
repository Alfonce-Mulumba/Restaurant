from django.shortcuts import render, redirect, get_object_or_404
from acaciaapp.models import *
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models import Q
from .forms import RegisterForm

# Registration
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully! Please login.")
        return redirect("login")  # 🔥 FIXED: do NOT go back to register

    return render(request, "register.html")

# Login
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")

            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)

            return redirect('/')

        return render(request, "login.html", {"error": "Invalid username or password"})

    next_url = request.GET.get('next', '')
    return render(request, "login.html", {"next": next_url})

# Logout
def logout_view(request):
    logout(request)
    return redirect("login")

# Reservation page
@login_required(login_url="login")
def reservations_view(request):
    if request.method == "POST":
        people = request.POST.get("people")
        date = request.POST.get("date")
        time = request.POST.get("time")
        message = request.POST.get("message")
        phone = request.POST.get("phone")

        Reservation.objects.create(
            user=request.user,
            reserved_name=request.user.get_full_name() or request.user.username,  # 🔥 Better name
            email=request.user.email,
            phone=phone,
            people=people,
            date=date,
            time=time,
            message=message
        )
        messages.success(request, 'Your reservation has been successfully booked!')
        return redirect("reservation")  # 🔥 FIXED: use URL name

    return render(request, 'reservation.html')


@login_required(login_url='login')
def profile_view(request):
    # Get all reservations for this user
    reservations = Reservation.objects.filter(user=request.user).order_by('-date', '-time')

    return render(request, 'profile.html', {
        'reservations': reservations
    })


@login_required(login_url='login')
def rooms_view(request):
    rooms = Room.objects.all().order_by('room_number')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    # No search: return all rooms but with status (occupied/vacant)
    if not check_in or not check_out:
        context = {
            "rooms": rooms,
            "check_in": "",
            "check_out": "",
            "search_mode": False
        }
        return render(request, "rooms.html", context)

    # Search mode
    try:
        check_in_date = timezone.datetime.strptime(check_in, "%Y-%m-%d").date()
        check_out_date = timezone.datetime.strptime(check_out, "%Y-%m-%d").date()
    except ValueError:
        messages.error(request, "Invalid date format.")
        return redirect("rooms")

    available_rooms = []
    for room in rooms:
        conflict = RoomBooking.objects.filter(
            room=room,
            check_in__lte=check_out_date,
            check_out__gte=check_in_date
        ).exists()

        if not conflict:
            available_rooms.append(room)

    context = {
        "rooms": available_rooms,
        "check_in": check_in,
        "check_out": check_out,
        "search_mode": True
    }
    return render(request, "rooms.html", context)

@property
def is_available(self):
    today = timezone.now().date()
    # Room is unavailable if it has a booking that includes today
    return not RoomBooking.objects.filter(
        room=self,
        check_in__lte=today,
        check_out__gte=today
    ).exists()


@login_required(login_url='login')
def book_room_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        age = request.POST.get('age')
        id_number = request.POST.get('id_number')
        people = request.POST.get('people')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        message = request.POST.get('message')

        # Conflict check
        conflicting = RoomBooking.objects.filter(
            room=room,
            check_in__lte=check_out,
            check_out__gte=check_in
        )
        if conflicting.exists():
            messages.error(request, "Room already booked for the selected dates.")
            return redirect('rooms')

        # Create booking
        RoomBooking.objects.create(
            user=request.user,
            room=room,
            customer_name=customer_name,
            email=email,
            phone=phone,
            age=age,
            id_number=id_number,
            people=people,
            check_in=check_in,
            check_out=check_out,
            message=message
        )

        messages.success(request, "Your room has been successfully booked!")
        return redirect('rooms')

    return render(request, 'book_room.html', {'room': room})



# Admin Dashboard
@staff_member_required(login_url='login')
def admin_dashboard(request):
    rooms = Room.objects.all().order_by('room_number')
    room_bookings = RoomBooking.objects.filter(is_cleared=False).order_by('-check_in')
    table_reservations = Reservation.objects.all().order_by('-date', '-time')

    # Handle room CRUD actions
    if request.method == "POST":
        if 'create_room' in request.POST:
            room_number = request.POST.get('room_number')
            capacity = request.POST.get('capacity')
            price = request.POST.get('price')
            description = request.POST.get('description')
            image = request.FILES.get('image')
            if Room.objects.filter(room_number=room_number).exists():
                messages.error(request, f"Room {room_number} already exists!")
            else:
                Room.objects.create(
                    room_number=room_number,
                    capacity=capacity,
                    price=price,
                    description=description,
                    image=image
                )
                messages.success(request, f"Room {room_number} created successfully!")

        elif 'toggle_room' in request.POST:
            room_id = request.POST.get('room_id')
            room = Room.objects.get(id=room_id)
            room.is_occupied = not room.is_occupied
            room.save()
            messages.success(request, f"Room {room.room_number} status updated.")

        elif 'clear_booking' in request.POST:
            booking_id = request.POST.get('booking_id')
            booking = RoomBooking.objects.get(id=booking_id)

            # 1. Mark as cleared → moves to "history"
            booking.is_cleared = True

            # 2. Free the room
            room = booking.room
            room.is_occupied = False
            room.save()

            # 3. Save booking changes
            booking.save()

            messages.success(request, f"Booking for {booking.customer_name} cleared successfully.")

    context = {
        'rooms': rooms,
        'room_bookings': room_bookings,
        'table_reservations': table_reservations
    }
    return render(request, 'admindashboard.html', context)


# Reservations
@staff_member_required(login_url='login')
def admin_reservations(request):
    reservations = Reservation.objects.all().order_by('-date', '-time')
    return render(request, 'admin_reservations.html', {'reservations': reservations})


# Rooms
@staff_member_required(login_url='login')
def admin_rooms(request):
    rooms = Room.objects.all().order_by('room_number')
    return render(request, 'admin_rooms.html', {'rooms': rooms})


# Mark Room Occupied/Vacant
@staff_member_required(login_url='login')
def toggle_room_status(request, room_id):
    room = Room.objects.get(id=room_id)
    room.is_occupied = not room.is_occupied
    room.save()
    messages.success(request, f"Room {room.room_number} status updated successfully.")
    return redirect('admin_rooms')


# Customers (Booked Rooms/Reservations)
@staff_member_required(login_url='login')
def admin_customers(request):
    room_bookings = RoomBooking.objects.all().order_by('-check_in')
    table_reservations = Reservation.objects.all().order_by('-date', '-time')
    context = {
        'room_bookings': room_bookings,
        'table_reservations': table_reservations
    }
    return render(request, 'admin_customers.html', context)


# Clear customer booking (e.g., check out)
@staff_member_required(login_url='login')
def clear_customer(request, booking_id):
    booking = RoomBooking.objects.get(id=booking_id)

    booking.is_cleared = True

    room = booking.room
    room.is_occupied = False
    room.save()

    booking.save()

    messages.success(request, f"Booking for {booking.customer_name} cleared successfully.")
    return redirect('admin_customers')


def index(request):
    return render(request, 'index.html')

def terms(request):
    return render(request, 'terms.html')

def privacy(request):
    return render(request, 'privacy.html')


def events(request):
    """
    Renders the events page and handles event booking form POST.
    Expect form fields: customer_name, email, phone, date, attendees, message, event_name (optional)
    """
    if request.method == "POST":
        customer_name = request.POST.get("customer_name") or request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        date_str = request.POST.get("date")
        attendees = request.POST.get("attendees") or request.POST.get("people") or 1
        message = request.POST.get("message", "")
        event_name = request.POST.get("event_name", "")

        # basic validation
        if not (customer_name and email and phone and date_str):
            messages.error(request, "Please fill all required fields.")
            return redirect("events")

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception:
            messages.error(request, "Invalid date format. Use YYYY-MM-DD.")
            return redirect("events")

        booking = EventBooking.objects.create(
            user = request.user if request.user.is_authenticated else None,
            customer_name = customer_name,
            email = email,
            phone = phone,
            date = date_obj,
            attendees = int(attendees) if str(attendees).isdigit() else 1,
            message = message,
            event_name = event_name
        )

        messages.success(request, "Your event booking has been received! We will contact you soon.")
        # optionally redirect to a confirmation page or back to events
        return redirect("events")

    # GET -> render page (you can add upcoming events context if you have an Event model)
    return render(request, "events.html")


def menu(request):
    return render(request, 'menu.html')

def about(request):
    return render(request, 'about.html')
