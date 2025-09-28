from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email должен быть указан')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField('Email', unique=True)

    # Дополнительные поля
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    current_language_level = models.CharField(
        'Текущий уровень языка',
        max_length=2,
        choices=[('A1', 'A1'), ('A2', 'A2'), ('B1', 'B1'),
                 ('B2', 'B2'), ('C1', 'C1'), ('C2', 'C2')],
        default='A1'
    )
    desired_language_level = models.CharField(
        'Желаемый уровень языка',
        max_length=2,
        choices=[('A1', 'A1'), ('A2', 'A2'), ('B1', 'B1'),
                 ('B2', 'B2'), ('C1', 'C1'), ('C2', 'C2')],
        default='A2'
    )
    phone_number = models.CharField('Номер телефона', max_length=20, blank=True)
    city = models.CharField('Город проживания', max_length=100, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class UserLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Вход в систему'),
        ('logout', 'Выход из системы'),
        ('register', 'Регистрация'),
        ('password_reset', 'Сброс пароля'),
        ('password_change', 'Изменение пароля'),
        ('profile_update', 'Обновление профиля'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    details = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Лог пользователя'
        verbose_name_plural = 'Логи пользователей'

    def __str__(self):
        return f"{self.user.email} - {self.get_action_display()} - {self.timestamp}"