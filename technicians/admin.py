from django.contrib import admin
from .models import TechnicianSchedule, TechnicianPerformance

@admin.register(TechnicianSchedule)
class TechnicianScheduleAdmin(admin.ModelAdmin):
    list_display = ['technician', 'date', 'start_time', 'end_time', 'is_work_day']

@admin.register(TechnicianPerformance)
class TechnicianPerformanceAdmin(admin.ModelAdmin):
    list_display = ['technician', 'date', 'completed_orders']
