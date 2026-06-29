from django.db import models
from django.conf import settings

class Review(models.Model):
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, verbose_name='订单', related_name='review')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户', related_name='reviews')
    rating = models.IntegerField('评分', choices=[(i, i) for i in range(1, 6)])
    content = models.TextField('评价内容', null=True, blank=True)
    image = models.ImageField('评价图片', upload_to='review_photos/', null=True, blank=True)
    reply_content = models.TextField('回复内容', null=True, blank=True)
    reply_time = models.DateTimeField('回复时间', null=True, blank=True)
    is_active = models.BooleanField('是否显示', default=True)
    created_at = models.DateTimeField('评价时间', auto_now_add=True)

    class Meta:
        verbose_name = '评价管理'
        verbose_name_plural = '评价管理'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order.order_no} - {self.rating}星'

class Complaint(models.Model):
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('resolved', '已解决'),
        ('closed', '已关闭'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='投诉人')
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='相关订单')
    title = models.CharField('标题', max_length=200)
    content = models.TextField('投诉内容')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    reply = models.TextField('处理回复', null=True, blank=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='处理人', related_name='processed_complaints')
    processed_at = models.DateTimeField('处理时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '投诉工单'
        verbose_name_plural = '投诉工单管理'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.get_status_display()}'
