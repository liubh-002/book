from django.db import models

class ServiceCategory(models.Model):
    name = models.CharField('分类名称', max_length=50)
    icon = models.CharField('图标', max_length=50, null=True, blank=True)
    sort_order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '服务分类'
        verbose_name_plural = '服务分类管理'
        ordering = ['sort_order']

    def __str__(self):
        return self.name

class ServiceItem(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, verbose_name='服务分类', related_name='services')
    name = models.CharField('服务名称', max_length=100)
    price = models.DecimalField('价格', max_digits=10, decimal_places=2)
    duration = models.IntegerField('服务时长(分钟)', default=60)
    description = models.TextField('服务详情', null=True, blank=True)
    applicable_pets = models.CharField('适用宠物', max_length=200, null=True, blank=True, help_text='如：适合所有犬种/猫')
    image = models.ImageField('服务图片', upload_to='service_photos/', null=True, blank=True)
    is_active = models.BooleanField('是否上架', default=True)
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '服务项目'
        verbose_name_plural = '服务项目管理'
        ordering = ['sort_order', 'category']

    def __str__(self):
        return f'{self.name} - ¥{self.price}'

class BusinessHours(models.Model):
    DAY_CHOICES = (
        (0, '周一'), (1, '周二'), (2, '周三'), (3, '周四'),
        (4, '周五'), (5, '周六'), (6, '周日'),
    )
    day_of_week = models.IntegerField('星期', choices=DAY_CHOICES)
    is_work_day = models.BooleanField('是否营业', default=True)
    start_time = models.TimeField('开始时间', default='09:00')
    end_time = models.TimeField('结束时间', default='18:00')
    slot_interval = models.IntegerField('时段间隔(分钟)', default=60)
    max_daily_bookings = models.IntegerField('每日最大预约量', default=50)

    class Meta:
        verbose_name = '营业时间'
        verbose_name_plural = '营业时间配置'
        ordering = ['day_of_week']

    def __str__(self):
        return f'{self.get_day_of_week_display()}: {self.start_time}-{self.end_time}'
