from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Deadline(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Низкая'),
        ('medium', 'Средняя'),
        ('high', 'Высокая'),
    ]
    
    COLOR_CHOICES = [
        ('#2196f3', 'Синий'),
        ('#4caf50', 'Зелёный'),
        ('#ff9800', 'Оранжевый'),
        ('#f44336', 'Красный'),
        ('#9c27b0', 'Фиолетовый'),
        ('#3f51b5', 'Индиго'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deadlines', verbose_name='Пользователь')
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    date = models.DateField(verbose_name='Дата')
    time = models.TimeField(default='23:59', verbose_name='Время')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name='Важность')
    color = models.CharField(max_length=7, choices=COLOR_CHOICES, default='#2196f3', verbose_name='Цвет')
    is_completed = models.BooleanField(default=False, verbose_name='Выполнено')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Дедлайн'
        verbose_name_plural = 'Дедлайны'
        ordering = ['date', 'time']
    
    def __str__(self):
        return f'{self.title} - {self.date} {self.time}'
    
    @property
    def is_overdue(self):
        """Проверяет, просрочен ли дедлайн"""
        from datetime import datetime
        deadline_datetime = datetime.combine(self.date, self.time)
        return timezone.now() > timezone.make_aware(deadline_datetime)
