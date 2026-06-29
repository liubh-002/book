from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta, date
from pets.models import Pet
from services.models import ServiceItem, BusinessHours
from orders.models import Order, OrderLog
from notifications.models import Notification
import random

@login_required
def book_appointment(request):
    pets = Pet.objects.filter(user=request.user, is_active=True)
    services = ServiceItem.objects.filter(is_active=True)
    
    if not pets.exists():
        messages.warning(request, '请先添加宠物档案再预约 🐱')
        return redirect('pets:add')
    
    if request.method == 'POST':
        pet_id = request.POST.get('pet_id')
        service_id = request.POST.get('service_id')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        notes = request.POST.get('notes', '')
        payment_method = request.POST.get('payment_method', 'store')
        
        pet = get_object_or_404(Pet, id=pet_id, user=request.user)
        service = get_object_or_404(ServiceItem, id=service_id, is_active=True)
        
        # Check for time slot conflict
        service_end = datetime.strptime(appointment_time, '%H:%M') + timedelta(minutes=service.duration)
        conflict = Order.objects.filter(
            appointment_date=appointment_date,
            status__in=['pending_confirm', 'confirmed', 'in_progress'],
        )
        
        for existing in conflict:
            existing_end = datetime.combine(
                datetime.strptime(str(existing.appointment_date), '%Y-%m-%d').date() 
                    if isinstance(existing.appointment_date, str) 
                    else existing.appointment_date,
                existing.appointment_time
            ) + timedelta(minutes=existing.service.duration if existing.service else 60)
            
            existing_start_time = existing.appointment_time
            if isinstance(existing_start_time, str):
                existing_start = datetime.strptime(existing_start_time, '%H:%M')
            else:
                existing_start = datetime.combine(date.today(), existing_start_time)
            
            existing_end = existing_start + timedelta(minutes=existing.service.duration if existing.service else 60)
            new_start = datetime.strptime(appointment_time, '%H:%M')
            new_end = new_start + timedelta(minutes=service.duration)
            
            if new_start < existing_end and new_end > existing_start:
                messages.error(request, '该时段已被预约，请选择其他时间 🕐')
                return render(request, 'appointments/book.html', {
                    'pets': pets, 'services': services,
                    'selected_pet': pet_id, 'selected_service': service_id,
                })
        
        # Create order
        order_no = f'PW{datetime.now().strftime("%Y%m%d%H%M%S")}{random.randint(100,999)}'
        order = Order.objects.create(
            user=request.user,
            pet=pet,
            service=service,
            order_no=order_no,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            amount=service.price,
            special_notes=notes,
            payment_method=payment_method,
            status='pending_confirm',
        )
        
        OrderLog.objects.create(
            order=order,
            operator=request.user,
            operation_type='created',
            content=f'用户预约洗护服务：{service.name}，时间：{appointment_date} {appointment_time}',
        )
        
        Notification.objects.create(
            user=request.user,
            notification_type='booking_success',
            title='预约提交成功 🎉',
            content=f'您的{service.name}预约已提交，等待商家确认',
            related_order=order,
        )
        
        messages.success(request, f'🎉 预约成功！订单号：{order_no}')
        return redirect('orders:my_orders')
    
    today = timezone.now().date()
    max_date = today + timedelta(days=30)
    
    # Generate available dates
    available_dates = []
    for i in range(30):
        d = today + timedelta(days=i)
        available_dates.append(d)
    
    return render(request, 'appointments/book.html', {
        'pets': pets,
        'services': services,
        'available_dates': available_dates,
        'today': today,
        'max_date': max_date,
    })

@login_required
def get_available_slots(request):
    from django.http import JsonResponse
    date_str = request.GET.get('date')
    service_id = request.GET.get('service_id')
    
    if not date_str or not service_id:
        return JsonResponse({'slots': []})
    
    try:
        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'slots': []})
    
    service = get_object_or_404(ServiceItem, id=service_id)
    
    # Get business hours for this day of week
    day_of_week = appointment_date.weekday()
    try:
        biz_hours = BusinessHours.objects.get(day_of_week=day_of_week, is_work_day=True)
    except BusinessHours.DoesNotExist:
        return JsonResponse({'slots': []})
    
    # Generate time slots
    slots = []
    current = datetime.combine(appointment_date, biz_hours.start_time)
    end = datetime.combine(appointment_date, biz_hours.end_time)
    
    while current + timedelta(minutes=service.duration) <= end:
        time_str = current.strftime('%H:%M')
        
        # Check existing bookings
        conflict = Order.objects.filter(
            appointment_date=appointment_date,
            appointment_time=current.time(),
            status__in=['pending_confirm', 'confirmed', 'in_progress', 'delayed'],
        )
        
        is_available = not conflict.exists()
        slots.append({
            'time': time_str,
            'available': is_available,
        })
        
        current += timedelta(minutes=biz_hours.slot_interval)
    
    return JsonResponse({'slots': slots})
