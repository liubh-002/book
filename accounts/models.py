from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', '普通客户'),
        ('technician', '洗护技师'),
        ('admin', '门店管理员'),
    )
    phone = models.CharField('手机号', max_length=20, unique=True, null=True, blank=True)
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='customer')
    avatar = models.ImageField('头像', upload_to='avatars/', null=True, blank=True)
    nickname = models.CharField('昵称', max_length=50, null=True, blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    login_attempts = models.IntegerField('登录尝试次数', default=0)
    locked_until = models.DateTimeField('锁定截止时间', null=True, blank=True)
    created_at = models.DateTimeField('注册时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户管理'
        ordering = ['-date_joined']

    def __str__(self):
        return self.nickname or self.username

class MemberLevel(models.Model):
    name = models.CharField('等级名称', max_length=50)
    min_spend = models.DecimalField('最低消费', max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField('折扣率', max_digits=4, decimal_places=2, default=1.0)
    points_rate = models.DecimalField('积分倍率', max_digits=4, decimal_places=2, default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '会员等级'
        verbose_name_plural = '会员等级管理'

    def __str__(self):
        return self.name

class Coupon(models.Model):
    COUPON_TYPES = (
        ('new_user', '新人券'),
        ('full_reduce', '满减券'),
        ('wash', '洗护专属券'),
    )
    name = models.CharField('优惠券名称', max_length=100)
    coupon_type = models.CharField('优惠券类型', max_length=20, choices=COUPON_TYPES)
    min_amount = models.DecimalField('最低消费金额', max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField('减免金额', max_digits=10, decimal_places=2)
    valid_days = models.IntegerField('有效天数', default=30)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '优惠券'
        verbose_name_plural = '优惠券管理'

    def __str__(self):
        return self.name

class UserCoupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, verbose_name='优惠券')
    is_used = models.BooleanField('是否已使用', default=False)
    used_at = models.DateTimeField('使用时间', null=True, blank=True)
    expires_at = models.DateTimeField('过期时间')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '用户优惠券'
        verbose_name_plural = '用户优惠券'

class LoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='用户')
    ip_address = models.CharField('IP地址', max_length=50, null=True, blank=True)
    login_time = models.DateTimeField('登录时间', auto_now_add=True)
    is_success = models.BooleanField('是否成功', default=True)

    class Meta:
        verbose_name = '登录日志'
        verbose_name_plural = '登录日志'
        ordering = ['-login_time']
