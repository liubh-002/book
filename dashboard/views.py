from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from datetime import timedelta
from orders.models import Order
from accounts.models import User

@login_required
def dashboard_index(request):
    if request.user.role not in ['admin']:
        from django.contrib import messages
        messages.error(request, '无权限访问')
        from django.shortcuts import redirect
        return redirect('/')
    
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    # Statistics
    today_orders = Order.objects.filter(appointment_date=today).count()
    today_completed = Order.objects.filter(completed_at__date=today, status='completed').count()
    pending_orders = Order.objects.filter(status__in=['pending_confirm', 'confirmed', 'delayed']).count()
    
    week_revenue = Order.objects.filter(
        completed_at__date__gte=week_start,
        status='completed',
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    month_revenue = Order.objects.filter(
        created_at__date__gte=month_start,
        status='completed',
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_users = User.objects.filter(role='customer', is_active=True).count()
    new_users_today = User.objects.filter(role='customer', date_joined__date=today).count()
    
    # Technician stats
    tech_stats = User.objects.filter(role='technician', is_active=True).annotate(
        order_count=Count('assigned_orders'),
        completed_count=Count('assigned_orders', filter=Order.objects.filter(status='completed').query),
    )
    
    # Recent orders
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    
    # Orders by status for chart
    status_data = {
        'pending_confirm': Order.objects.filter(status='pending_confirm').count(),
        'confirmed': Order.objects.filter(status='confirmed').count(),
        'in_progress': Order.objects.filter(status='in_progress').count(),
        'completed': Order.objects.filter(status='completed').count(),
        'cancelled': Order.objects.filter(status='cancelled').count(),
    }
    
    # Today hourly orders for chart
    hourly_orders = []
    for h in range(8, 20):
        hourly_orders.append(Order.objects.filter(
            appointment_date=today,
            appointment_time__hour=h,
        ).count())
    
    return render(request, 'dashboard/index.html', {
        'today_orders': today_orders,
        'today_completed': today_completed,
        'pending_orders': pending_orders,
        'week_revenue': week_revenue,
        'month_revenue': month_revenue,
        'total_users': total_users,
        'new_users_today': new_users_today,
        'tech_stats': tech_stats,
        'recent_orders': recent_orders,
        'status_data': status_data,
        'hourly_orders': hourly_orders,
    })
