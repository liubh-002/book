from django.db import models
from django.conf import settings

class TechnicianSchedule(models.Model):
    technician = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='技师', related_name='schedules')
    date = models.DateField('日期')
    start_time = models.TimeField('上班时间')
    end_time = models.TimeField('下班时间')
    is_work_day = models.BooleanField('是否上班', default=True)
    max_orders = models.IntegerField('最大接单量', default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '技师排班'
        verbose_name_plural = '技师排班管理'
        unique_together = ['technician', 'date']
        ordering = ['-date']

    def __str__(self):
        return f'{self.technician.nickname or self.technician.username} - {self.date}'

class TechnicianPerformance(models.Model):
    technician = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='技师', related_name='performance')
    date = models.DateField('日期')
    completed_orders = models.IntegerField('完成订单数', default=0)
    total_orders = models.IntegerField('总接单数', default=0)
    avg_rating = models.DecimalField('平均评分', max_digits=3, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '技师绩效'
        verbose_name_plural = '技师绩效管理'
        unique_together = ['technician', 'date']
        ordering = ['-date']
