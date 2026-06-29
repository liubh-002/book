from django.contrib import admin
from .models import User, MemberLevel, Coupon, UserCoupon, LoginLog

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'nickname', 'phone', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'nickname', 'phone']
    ordering = ['-date_joined']

@admin.register(MemberLevel)
class MemberLevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'min_spend', 'discount']

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['name', 'coupon_type', 'discount_amount', 'is_active']

@admin.register(UserCoupon)
class UserCouponAdmin(admin.ModelAdmin):
    list_display = ['user', 'coupon', 'is_used', 'expires_at']

@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'login_time', 'is_success']
