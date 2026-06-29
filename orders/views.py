from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from .models import Order, OrderLog
from notifications.models import Notification
from accounts.models import User

@login_required
def my_orders(request):
    status_filter = request.GET.get('status', 'all')
    orders = Order.objects.filter(user=request.user)
    if status_filter != 'all':
        orders = orders.filter(status=status_filter)
    # Auto complete after 24h
    for order in orders.filter(status='pending_acceptance'):
        if order.actual_end_time and timezone.now() > order.actual_end_time + timezone.timedelta(hours=24):
            order.status = 'completed'
            order.save()
    return render(request, 'orders/my_orders.html', {'orders': orders, 'status_filter': status_filter})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    logs = OrderLog.objects.filter(order=order)
    return render(request, 'orders/detail.html', {'order': order, 'logs': logs})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status not in ['pending_confirm', 'confirmed']:
        messages.error(request, '当前订单状态不可取消')
        return redirect('orders:my_orders')
    order.status = 'cancelled'
    order.cancel_reason = '用户主动取消'
    order.save()
    OrderLog.objects.create(order=order, operator=request.user, operation_type='cancelled', content='用户主动取消订单')
    messages.success(request, '订单已取消')
    return redirect('orders:my_orders')

@login_required
def accept_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status != 'pending_acceptance':
        messages.error(request, '订单状态不正确')
        return redirect('orders:my_orders')
    order.status = 'completed'
    order.completed_at = timezone.now()
    order.save()
    OrderLog.objects.create(order=order, operator=request.user, operation_type='accepted', content='用户确认验收')
    messages.success(request, '🎉 验收成功！欢迎下次光临~')
    return redirect('orders:my_orders')

# Admin
@login_required
def admin_order_list(request):
    if request.user.role not in ['admin']:
        messages.error(request, '无权限访问')
        return redirect('/')
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    orders = Order.objects.all()
    if status_filter:
        orders = orders.filter(status=status_filter)
    if search:
        orders = orders.filter(Q(order_no__icontains=search) | Q(user__nickname__icontains=search) | Q(user__username__icontains=search) | Q(pet__name__icontains=search))
    technicians = User.objects.filter(role='technician', is_active=True)
    return render(request, 'orders/admin_list.html', {
        'orders': orders, 'status_filter': status_filter, 'search': search, 'technicians': technicians,
    })

@login_required
def admin_confirm_order(request, order_id):
    if request.user.role != 'admin': return redirect('/')
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'confirm':
            order.status = 'confirmed'; order.save()
            OrderLog.objects.create(order=order, operator=request.user, operation_type='confirmed', content='管理员确认接单')
            Notification.objects.create(user=order.user, notification_type='booking_success', title='预约已确认 ✅', content=f'您的{order.service.name}预约已被商家确认', related_order=order)
            messages.success(request, '已确认接单')
        elif action == 'reject':
            reason = request.POST.get('reject_reason', '')
            order.status = 'cancelled'; order.reject_reason = reason; order.save()
            OrderLog.objects.create(order=order, operator=request.user, operation_type='rejected', content=f'驳回原因：{reason}')
            Notification.objects.create(user=order.user, notification_type='order_cancelled', title='预约已被驳回', content=f'原因：{reason}', related_order=order)
            messages.success(request, '已驳回订单')
    return redirect('orders:admin_list')

@login_required
def admin_reschedule(request, order_id):
    if request.user.role != 'admin': return redirect('/')
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_date = request.POST.get('new_date'); new_time = request.POST.get('new_time')
        if new_date and new_time:
            conflict = Order.objects.filter(appointment_date=new_date, appointment_time=new_time, status__in=['pending_confirm','confirmed','in_progress','delayed']).exclude(id=order.id)
            if conflict.exists():
                messages.error(request, '该时段已被占用')
                return redirect('orders:admin_list')
            old_date = order.appointment_date; old_time = order.appointment_time
            order.appointment_date = new_date; order.appointment_time = new_time; order.status = 'confirmed'; order.save()
            OrderLog.objects.create(order=order, operator=request.user, operation_type='rescheduled', content=f'改期：从{old_date} {old_time} 改为 {new_date} {new_time}')
            Notification.objects.create(user=order.user, notification_type='order_rescheduled', title='订单已改期 📅', content=f'预约已从{old_date} {old_time} 改为 {new_date} {new_time}', related_order=order)
            messages.success(request, '改期成功')
    return redirect('orders:admin_list')

@login_required
def admin_delay(request, order_id):
    if request.user.role != 'admin': return redirect('/')
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        delay_minutes = int(request.POST.get('delay_minutes', 30))
        reason = request.POST.get('delay_reason', '')
        from datetime import datetime, timedelta
        current_time = datetime.combine(order.appointment_date, order.appointment_time)
        new_time = current_time + timedelta(minutes=delay_minutes)
        order.appointment_time = new_time.time()
        if new_time.date() != order.appointment_date:
            order.appointment_date = new_time.date()
        order.status = 'delayed'; order.delay_count += 1; order.delay_reason = reason; order.save()
        OrderLog.objects.create(order=order, operator=request.user, operation_type='delayed', content=f'延后{delay_minutes}分钟，原因：{reason}')
        Notification.objects.create(user=order.user, notification_type='order_delayed', title='订单已延后 ⏰', content=f'预约已延后{delay_minutes}分钟', related_order=order)
        messages.success(request, f'已延后{delay_minutes}分钟')
    return redirect('orders:admin_list')

@login_required
def admin_assign_technician(request, order_id):
    if request.user.role != 'admin': return redirect('/')
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        tech_id = request.POST.get('technician_id')
        if tech_id:
            technician = get_object_or_404(User, id=tech_id, role='technician')
            order.technician = technician; order.save()
            OrderLog.objects.create(order=order, operator=request.user, operation_type='assigned', content=f'指派技师：{technician.nickname or technician.username}')
            Notification.objects.create(user=technician, notification_type='technician_assigned', title='新订单指派 🛠️', content=f'您被指派了订单{order.order_no}', related_order=order)
            messages.success(request, f'已指派技师：{technician.nickname or technician.username}')
    return redirect('orders:admin_list')

@login_required
def admin_cancel_order(request, order_id):
    if request.user.role != 'admin': return redirect('/')
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        reason = request.POST.get('cancel_reason', '管理员取消')
        order.status = 'cancelled'; order.cancel_reason = reason; order.save()
        OrderLog.objects.create(order=order, operator=request.user, operation_type='cancelled', content=f'管理员取消，原因：{reason}')
        Notification.objects.create(user=order.user, notification_type='order_cancelled', title='订单已取消', content=f'您的订单已被管理员取消，原因：{reason}', related_order=order)
        messages.success(request, '订单已取消')
    return redirect('orders:admin_list')

@login_required
def admin_toggle_lock(request, order_id):
    if request.user.role != 'admin': return redirect('/')
    order = get_object_or_404(Order, id=order_id)
    if order.is_locked:
        order.is_locked = False; order.locked_by = None; order.status = 'confirmed'
        OrderLog.objects.create(order=order, operator=request.user, operation_type='unlocked', content='解冻订单')
        messages.success(request, '订单已解冻')
    else:
        order.is_locked = True; order.locked_by = request.user; order.status = 'locked'
        OrderLog.objects.create(order=order, operator=request.user, operation_type='locked', content='锁定订单')
        messages.success(request, '订单已锁定')
    order.save()
    return redirect('orders:admin_list')

# Technician
@login_required
def technician_orders(request):
    if request.user.role != 'technician':
        messages.error(request, '无权限访问')
        return redirect('/')
    status_filter = request.GET.get('status', '')
    orders = Order.objects.filter(technician=request.user)
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'orders/technician_orders.html', {'orders': orders, 'status_filter': status_filter})

@login_required
def technician_update_status(request, order_id):
    if request.user.role != 'technician': return redirect('/')
    order = get_object_or_404(Order, id=order_id, technician=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'start' and order.status == 'confirmed':
            order.status = 'in_progress'; order.actual_start_time = timezone.now(); order.save()
            OrderLog.objects.create(order=order, operator=request.user, operation_type='started', content='技师开始服务')
            Notification.objects.create(user=order.user, notification_type='service_start', title='洗护开始 🛁', content=f'您的{order.pet.name}已经开始洗护啦~', related_order=order)
            messages.success(request, '已开始服务')
        elif action == 'complete' and order.status == 'in_progress':
            order.status = 'pending_acceptance'; order.actual_end_time = timezone.now()
            order.service_notes = request.POST.get('service_notes', ''); order.save()
            OrderLog.objects.create(order=order, operator=request.user, operation_type='completed', content='技师完成服务')
            Notification.objects.create(user=order.user, notification_type='service_complete', title='洗护完成 ✨', content=f'{order.pet.name}的洗护已完成，请来验收~', related_order=order)
            messages.success(request, '服务已完成，等待用户验收')
    return redirect('orders:technician_orders')
