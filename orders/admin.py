from django.contrib import admin
from .models import Order, OrderLog

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_no', 'user', 'service', 'appointment_date', 'status', 'amount', 'created_at']
    list_filter = ['status', 'appointment_date', 'service']
    search_fields = ['order_no', 'user__username', 'pet__name']
    date_hierarchy = 'appointment_date'
    fieldsets = (
        ('基本信息', {'fields': ('order_no', 'user', 'pet', 'service', 'technician')}),
        ('时间信息', {'fields': ('appointment_date', 'appointment_time', 'actual_start_time', 'actual_end_time')}),
        ('金额信息', {'fields': ('amount', 'payment_method')}),
        ('状态信息', {'fields': ('status', 'is_locked', 'locked_by')}),
        ('备注信息', {'fields': ('special_notes', 'cancel_reason', 'delay_reason', 'reject_reason', 'service_notes')}),
        ('照片', {'fields': ('before_photos', 'after_photos')}),
    )

@admin.register(OrderLog)
class OrderLogAdmin(admin.ModelAdmin):
    list_display = ['order', 'operator', 'operation_type', 'created_at']
    list_filter = ['operation_type']
    search_fields = ['order__order_no']
