from django.contrib import admin
from .models import ServiceCategory, ServiceItem, BusinessHours

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'sort_order', 'is_active']

@admin.register(ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'duration', 'is_active']
    list_filter = ['category', 'is_active']

@admin.register(BusinessHours)
class BusinessHoursAdmin(admin.ModelAdmin):
    list_display = ['day_of_week', 'is_work_day', 'start_time', 'end_time']
