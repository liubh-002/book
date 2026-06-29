from django.urls import path, include
from . import views

app_name = 'appointments'
urlpatterns = [
    path('book/', views.book_appointment, name='book'),
    path('api/slots/', views.get_available_slots, name='get_slots'),
]
