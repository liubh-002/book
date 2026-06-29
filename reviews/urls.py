from django.urls import path
from . import views

app_name = 'reviews'
urlpatterns = [
    path('create/<int:order_id>/', views.create_review, name='create'),
    path('list/', views.reviews_list, name='list'),
    path('<int:review_id>/reply/', views.admin_reply_review, name='admin_reply'),
    path('complaint/', views.create_complaint, name='complaint'),
]
