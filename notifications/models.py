from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('booking_success', '预约成功'),
        ('order_rescheduled', '订单改期'),
        ('order_delayed', '订单延后'),
        ('service_start', '服务开始'),
        ('service_complete', '服务完成'),
        ('order_cancelled', '订单取消'),
        ('technician_assigned', '技师接单'),
        ('reminder', '到期提醒'),
        ('system', '系统公告'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='接收用户', related_name='notifications')
    notification_type = models.CharField('通知类型', max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容', null=True, blank=True)
    related_order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='相关订单')
    is_read = models.BooleanField('是否已读', default=False)
    read_at = models.DateTimeField('阅读时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '消息通知'
        verbose_name_plural = '消息通知管理'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_notification_type_display()} - {self.title}'
