from django.urls import path
from . import views

app_name = 'orders'
urlpatterns = [
    # Customer
    path('my/', views.my_orders, name='my_orders'),
    path('<int:order_id>/', views.order_detail, name='detail'),
    path('<int:order_id>/cancel/', views.cancel_order, name='cancel'),
    path('<int:order_id>/accept/', views.accept_order, name='accept'),
    # Admin
    path('admin/list/', views.admin_order_list, name='admin_list'),
    path('admin/<int:order_id>/confirm/', views.admin_confirm_order, name='admin_confirm'),
    path('admin/<int:order_id>/reschedule/', views.admin_reschedule, name='admin_reschedule'),
    path('admin/<int:order_id>/delay/', views.admin_delay, name='admin_delay'),
    path('admin/<int:order_id>/assign/', views.admin_assign_technician, name='admin_assign'),
    path('admin/<int:order_id>/cancel-order/', views.admin_cancel_order, name='admin_cancel'),
    path('admin/<int:order_id>/toggle-lock/', views.admin_toggle_lock, name='admin_toggle_lock'),
    # Technician
    path('technician/', views.technician_orders, name='technician_orders'),
    path('technician/<int:order_id>/update/', views.technician_update_status, name='technician_update'),
]
