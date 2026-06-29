from django.db import models
from django.conf import settings

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending_confirm', '待商家确认'),
        ('confirmed', '预约成功'),
        ('delayed', '订单延后'),
        ('in_progress', '洗护进行中'),
        ('pending_acceptance', '待验收'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('locked', '已锁定'),
    )
    PAYMENT_CHOICES = (
        ('online', '线上预付'),
        ('store', '到店付款'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='客户', related_name='orders')
    pet = models.ForeignKey('pets.Pet', on_delete=models.SET_NULL, null=True, verbose_name='宠物')
    technician = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='技师', related_name='assigned_orders')
    service = models.ForeignKey('services.ServiceItem', on_delete=models.SET_NULL, null=True, verbose_name='洗护服务')
    order_no = models.CharField('订单号', max_length=50, unique=True)
    appointment_date = models.DateField('预约日期')
    appointment_time = models.TimeField('预约时间')
    actual_start_time = models.DateTimeField('实际开始时间', null=True, blank=True)
    actual_end_time = models.DateTimeField('实际结束时间', null=True, blank=True)
    status = models.CharField('订单状态', max_length=30, choices=STATUS_CHOICES, default='pending_confirm')
    payment_method = models.CharField('支付方式', max_length=10, choices=PAYMENT_CHOICES, default='store')
    amount = models.DecimalField('订单金额', max_digits=10, decimal_places=2)
    special_notes = models.TextField('特殊备注', null=True, blank=True)
    cancel_reason = models.TextField('取消原因', null=True, blank=True)
    delay_reason = models.TextField('延后原因', null=True, blank=True)
    delay_count = models.IntegerField('延后次数', default=0)
    reject_reason = models.TextField('驳回原因', null=True, blank=True)
    before_photos = models.ImageField('洗护前照片', upload_to='service_photos/', null=True, blank=True)
    after_photos = models.ImageField('洗护后照片', upload_to='service_photos/', null=True, blank=True)
    service_notes = models.TextField('服务记录', null=True, blank=True)
    is_locked = models.BooleanField('是否锁定', default=False)
    locked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='锁定人', related_name='locked_orders')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单管理'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order_no} - {self.get_status_display()}'

class OrderLog(models.Model):
    OPERATION_CHOICES = (
        ('created', '创建订单'),
        ('confirmed', '确认接单'),
        ('rejected', '驳回预约'),
        ('rescheduled', '改期'),
        ('delayed', '延后'),
        ('assigned', '指派技师'),
        ('reassigned', '更换技师'),
        ('started', '开始服务'),
        ('completed', '完成服务'),
        ('cancelled', '取消订单'),
        ('locked', '锁定订单'),
        ('unlocked', '解冻订单'),
        ('accepted', '验收完成'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='订单', related_name='logs')
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='操作人')
    operation_type = models.CharField('操作类型', max_length=30, choices=OPERATION_CHOICES)
    content = models.TextField('操作内容', null=True, blank=True)
    created_at = models.DateTimeField('操作时间', auto_now_add=True)

    class Meta:
        verbose_name = '订单操作日志'
        verbose_name_plural = '订单操作日志'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order.order_no} - {self.get_operation_type_display()}'
