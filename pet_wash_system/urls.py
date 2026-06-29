from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.http import JsonResponse
from services.models import ServiceItem, ServiceCategory
from orders.models import Order
from reviews.models import Review
from django.utils import timezone
from datetime import timedelta


def health_check(request):
    return JsonResponse({'status': 'ok'}, status=200)


def homepage(request):
    services = ServiceItem.objects.filter(is_active=True)[:6]
    reviews = Review.objects.filter(is_active=True).order_by('-created_at')[:4]
    today = timezone.now().date()
    today_orders = Order.objects.filter(appointment_date=today).count()

    return render(request, 'home.html', {
        'services': services,
        'reviews': reviews,
        'today_orders': today_orders,
    })


urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    path('', homepage, name='home'),
    path('accounts/', include('accounts.urls')),
    path('pets/', include('pets.urls')),
    path('services/', include('services.urls')),
    path('appointments/', include('appointments.urls')),
    path('orders/', include('orders.urls')),
    path('reviews/', include('reviews.urls')),
    path('notifications/', include('notifications.urls')),
    path('dashboard/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
