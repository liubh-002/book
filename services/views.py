from django.shortcuts import render
from django.contrib import messages
from .models import ServiceItem, ServiceCategory

def service_list(request):
    categories = ServiceCategory.objects.filter(is_active=True).prefetch_related('services')
    services = ServiceItem.objects.filter(is_active=True)
    return render(request, 'services/list.html', {
        'categories': categories,
        'services': services,
    })
