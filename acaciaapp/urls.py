
from django.contrib import admin
from django.urls import path
from acaciaapp import views

urlpatterns = [
    path('', views.index, name="index"),
    path('terms/', views.terms, name="terms"),
    path('privacy/', views.privacy, name="privacy"),
    path('reservation/', views.reservations_view, name="reservation"),
    path('events/', views.events, name="events"),

    path('menu/', views.menu, name="menu"),
    path('about/', views.about, name="about"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path('profile/', views.profile_view, name='profile'),
    path('rooms/', views.rooms_view, name='rooms'),
    path('rooms/book/<int:room_id>/', views.book_room_view, name='book_room'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/reservations/', views.admin_reservations, name='admin_reservations'),
    path('admin/rooms/', views.admin_rooms, name='admin_rooms'),
    path('admin/rooms/toggle/<int:room_id>/', views.toggle_room_status, name='toggle_room_status'),
    path('admin/customers/', views.admin_customers, name='admin_customers'),
    path('admin/customers/clear/<int:booking_id>/', views.clear_customer, name='clear_customer'),
]
