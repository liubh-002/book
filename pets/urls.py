from django.urls import path
from . import views

app_name = 'pets'
urlpatterns = [
    path('', views.pet_list, name='list'),
    path('add/', views.pet_add, name='add'),
    path('<int:pet_id>/edit/', views.pet_edit, name='edit'),
    path('<int:pet_id>/delete/', views.pet_delete, name='delete'),
    path('<int:pet_id>/set-default/', views.pet_set_default, name='set_default'),
]
