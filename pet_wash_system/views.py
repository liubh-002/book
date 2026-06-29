from django.shortcuts import render
from django.http import JsonResponse


def health_check(request):
    """轻量健康检查端点 — 无数据库依赖，始终可用"""
    return JsonResponse({'status': 'ok'}, status=200)


def homepage(request):
    """首页 — 使用惰性导入避免启动时数据库依赖"""
    from django.utils import timezone
    from services.models import ServiceItem
    from orders.models import Order
    from reviews.models import Review

    services = ServiceItem.objects.filter(is_active=True)[:6]
    reviews = Review.objects.filter(is_active=True).order_by('-created_at')[:4]
    today = timezone.now().date()
    today_orders = Order.objects.filter(appointment_date=today).count()

    return render(request, 'home.html', {
        'services': services,
        'reviews': reviews,
        'today_orders': today_orders,
    })
