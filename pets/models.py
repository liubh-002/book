from django.db import models
from django.conf import settings

class Pet(models.Model):
    GENDER_CHOICES = (
        ('male', '男孩子'),
        ('female', '女孩子'),
    )
    SIZE_CHOICES = (
        ('small', '小型'),
        ('medium', '中型'),
        ('large', '大型'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='主人', related_name='pets')
    name = models.CharField('宠物昵称', max_length=50)
    breed = models.CharField('品种', max_length=100, null=True, blank=True)
    gender = models.CharField('性别', max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    age = models.IntegerField('年龄(月)', null=True, blank=True)
    weight = models.DecimalField('体重(kg)', max_digits=5, decimal_places=1, null=True, blank=True)
    color = models.CharField('毛色', max_length=50, null=True, blank=True)
    size = models.CharField('体型', max_length=10, choices=SIZE_CHOICES, default='small')
    avatar = models.ImageField('宠物照片', upload_to='pet_photos/', null=True, blank=True)
    vaccination = models.TextField('疫苗接种记录', null=True, blank=True)
    deworming = models.TextField('驱虫记录', null=True, blank=True)
    allergies = models.TextField('过敏史', null=True, blank=True, help_text='如皮肤过敏、食物过敏等')
    medical_history = models.TextField('既往病史', null=True, blank=True)
    taboos = models.TextField('特殊禁忌', null=True, blank=True, help_text='怕水、怕吹风机、攻击性强等')
    personality = models.TextField('宠物性格', null=True, blank=True)
    notes = models.TextField('洗护注意事项', null=True, blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    is_default = models.BooleanField('是否默认宠物', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '宠物档案'
        verbose_name_plural = '宠物档案管理'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f'{self.name}({self.user.nickname or self.user.username})'
