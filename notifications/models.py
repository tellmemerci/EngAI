from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('info', 'Информация'),
        ('success', 'Успех'),
        ('warning', 'Предупреждение'),
        ('error', 'Ошибка'),
        ('achievement', 'Достижение'),
        ('message', 'Сообщение'),
        ('update', 'Обновление'),
    ]

    ICON_MAPPING = {
        'info': 'bi-info-circle',
        'success': 'bi-check-circle',
        'warning': 'bi-exclamation-triangle',
        'error': 'bi-x-circle',
        'achievement': 'bi-trophy',
        'message': 'bi-chat-dots',
        'update': 'bi-arrow-clockwise',
    }

    COLOR_MAPPING = {
        'info': '#3498db',
        'success': '#2ecc71',
        'warning': '#f1c40f',
        'error': '#e74c3c',
        'achievement': '#9b59b6',
        'message': '#1abc9c',
        'update': '#34495e',
    }

    title = models.CharField(max_length=200, verbose_name='Название')
    text = models.TextField(verbose_name='Текст уведомления')
    image = models.ImageField(upload_to='notifications/', blank=True, null=True, verbose_name='Изображение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='Пользователь')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='info',
        verbose_name='Тип уведомления'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def __str__(self):
        if self.created_at:
            return f"{self.title} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"
        return self.title

    @property
    def icon_class(self):
        return self.ICON_MAPPING.get(self.notification_type, 'bi-bell')

    @property
    def color(self):
        return self.COLOR_MAPPING.get(self.notification_type, '#3498db')
