from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
import os

def module_image_path(instance, filename):
    """Функция для определения пути сохранения изображения модуля"""
    # Получаем расширение файла
    ext = filename.split('.')[-1]
    # Формируем имя файла из timestamp и id модуля (если есть)
    filename = f"{int(timezone.now().timestamp())}"
    if instance.pk:
        filename = f"{filename}_{instance.pk}"
    # Возвращаем путь: study_modules/YYYY/MM/filename.ext
    return f'study_modules/{timezone.now().strftime("%Y/%m")}/{filename}.{ext}'

class StudyModule(models.Model):
    MODULE_TYPES = (
        ('free', 'Бесплатный'),
        ('premium', 'Премиум'),
        ('locked', 'Закрытый'),
    )

    # Явно определяем менеджер
    objects = models.Manager()

    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(
        upload_to=module_image_path,
        null=True,
        blank=True,
        verbose_name='Изображение',
        help_text='Рекомендуемый размер: 1200x800 пикселей'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_modules',
        verbose_name='Автор'
    )
    module_type = models.CharField(
        max_length=10,
        choices=MODULE_TYPES,
        default='free',
        verbose_name='Тип модуля'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_published = models.BooleanField(default=False, verbose_name='Опубликован')
    access_password = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Пароль доступа',
        help_text='Пароль для доступа к закрытому модулю'
    )

    saved_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='saved_modules',
        blank=True,
        verbose_name='Сохранено пользователями'
    )

    class Meta:
        verbose_name = 'Учебный модуль'
        verbose_name_plural = 'Учебные модули'
        ordering = ['-created_at']
        default_manager_name = 'objects'

    def __str__(self):
        return self.title

    @property
    def is_available(self):
        """Проверяет доступность модуля"""
        if self.module_type == 'locked':
            return False
        return self.module_type == 'free' or self.is_published
    
    def set_password(self, raw_password):
        """Устанавливает пароль для модуля"""
        if raw_password:
            self.access_password = make_password(raw_password)
        else:
            self.access_password = None
    
    def check_password(self, raw_password):
        """Проверяет пароль модуля"""
        if not self.access_password:
            return False
        return check_password(raw_password, self.access_password)
    
    def has_password(self):
        """Проверяет, установлен ли пароль для модуля"""
        return bool(self.access_password)

    def save(self, *args, **kwargs):
        """Переопределяем сохранение для удаления старого изображения"""
        if self.pk:
            try:
                old_instance = StudyModule.objects.get(pk=self.pk)
                if old_instance.image and self.image != old_instance.image:
                    # Удаляем старое изображение
                    if os.path.isfile(old_instance.image.path):
                        os.remove(old_instance.image.path)
            except StudyModule.DoesNotExist:
                pass
        super().save(*args, **kwargs)


class ModuleSection(models.Model):
    """Секции модуля (теория, практика)"""
    SECTION_TYPES = (
        ('theory', 'Теоретическая часть'),
        ('practice', 'Практическая часть'),
    )
    
    module = models.ForeignKey(StudyModule, on_delete=models.CASCADE, related_name='sections', verbose_name='Модуль')
    section_type = models.CharField(max_length=10, choices=SECTION_TYPES, verbose_name='Тип секции')
    title = models.CharField(max_length=200, verbose_name='Название секции')
    description = models.TextField(blank=True, verbose_name='Описание секции')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Секция модуля'
        verbose_name_plural = 'Секции модулей'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.module.title} - {self.title}"


class ModuleSkill(models.Model):
    """Навыки модуля (Listening, Writing, Grammar и т.д.)"""
    SKILL_TYPES = (
        ('listening', 'Listening'),
        ('writing', 'Writing'),
        ('grammar', 'Grammar'),
        ('reading', 'Reading'),
        ('speaking', 'Speaking'),
        ('words', 'Words'),
        ('watching', 'Watching'),
        ('test', 'Test'),
    )
    
    module = models.ForeignKey(StudyModule, on_delete=models.CASCADE, related_name='skills', verbose_name='Модуль')
    skill_type = models.CharField(max_length=20, choices=SKILL_TYPES, verbose_name='Тип навыка')
    title = models.CharField(max_length=200, verbose_name='Название навыка')
    description = models.TextField(blank=True, verbose_name='Описание навыка')
    is_available = models.BooleanField(default=True, verbose_name='Доступен')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Навык модуля'
        verbose_name_plural = 'Навыки модулей'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.module.title} - {self.title}"


class TheoryCard(models.Model):
    """Теоретические карточки"""
    section = models.ForeignKey(ModuleSection, on_delete=models.CASCADE, related_name='theory_cards', verbose_name='Секция')
    title = models.CharField(max_length=200, verbose_name='Название карточки')
    content = models.TextField(blank=True, verbose_name='Содержание карточки')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Теоретическая карточка'
        verbose_name_plural = 'Теоретические карточки'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.section.title} - {self.title}"


class ModuleAttachment(models.Model):
    """Прикрепленные файлы к модулю"""
    FILE_TYPES = (
        ('pdf', 'PDF'),
        ('audio', 'Аудио'),
        ('doc', 'Документ'),
        ('image', 'Изображение'),
        ('video', 'Видео'),
        ('other', 'Другое'),
    )
    
    module = models.ForeignKey(StudyModule, on_delete=models.CASCADE, related_name='attachments', verbose_name='Модуль')
    file_type = models.CharField(max_length=10, choices=FILE_TYPES, verbose_name='Тип файла')
    title = models.CharField(max_length=200, verbose_name='Название файла')
    file = models.FileField(upload_to='module_attachments/', verbose_name='Файл')
    description = models.CharField(max_length=500, blank=True, verbose_name='Описание файла')
    file_size = models.CharField(max_length=50, blank=True, verbose_name='Размер файла')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Прикрепленный файл'
        verbose_name_plural = 'Прикрепленные файлы'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.module.title} - {self.title}"


def unit_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{int(timezone.now().timestamp())}"
    if instance.pk:
        filename = f"{filename}_{instance.pk}"
    return f'study_modules/units/{timezone.now().strftime("%Y/%m")}/{filename}.{ext}'


class Unit(models.Model):
    module = models.ForeignKey(StudyModule, on_delete=models.CASCADE, related_name='units', verbose_name='Модуль')
    title = models.CharField(max_length=200, verbose_name='Название юнита')
    description = models.TextField(blank=True, verbose_name='Описание юнита')
    image = models.ImageField(upload_to=unit_image_path, null=True, blank=True, verbose_name='Изображение юнита')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Юнит'
        verbose_name_plural = 'Юниты'
        ordering = ['order']

    def __str__(self):
        return f"{self.module.title} - {self.title}"


class UnitSection(models.Model):
    """Секции юнита (теория, практика)"""
    SECTION_TYPES = (
        ('theory', 'Теоретическая часть'),
        ('practice', 'Практическая часть'),
    )
    
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='sections', verbose_name='Юнит')
    section_type = models.CharField(max_length=10, choices=SECTION_TYPES, verbose_name='Тип секции')
    title = models.CharField(max_length=200, verbose_name='Название секции')
    description = models.TextField(blank=True, verbose_name='Описание секции')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Секция юнита'
        verbose_name_plural = 'Секции юнитов'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.unit.title} - {self.title}"


class UnitSkill(models.Model):
    """Навыки юнита (Listening, Writing, Grammar и т.д.)"""
    SKILL_TYPES = (
        ('listening', 'Listening'),
        ('writing', 'Writing'),
        ('grammar', 'Grammar'),
        ('reading', 'Reading'),
        ('speaking', 'Speaking'),
        ('words', 'Words'),
        ('watching', 'Watching'),
        ('test', 'Test'),
    )
    
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='skills', verbose_name='Юнит')
    skill_type = models.CharField(max_length=20, choices=SKILL_TYPES, verbose_name='Тип навыка')
    title = models.CharField(max_length=200, verbose_name='Название навыка')
    description = models.TextField(blank=True, verbose_name='Описание навыка')
    is_available = models.BooleanField(default=True, verbose_name='Доступен')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Навык юнита'
        verbose_name_plural = 'Навыки юнитов'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.unit.title} - {self.title}"


class UnitTheoryCard(models.Model):
    """Теоретические карточки юнита"""
    section = models.ForeignKey(UnitSection, on_delete=models.CASCADE, related_name='theory_cards', verbose_name='Секция')
    title = models.CharField(max_length=200, verbose_name='Название карточки')
    content = models.TextField(blank=True, verbose_name='Содержание карточки')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Теоретическая карточка юнита'
        verbose_name_plural = 'Теоретические карточки юнитов'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.section.title} - {self.title}"


class UnitAttachment(models.Model):
    """Прикрепленные файлы к юниту"""
    FILE_TYPES = (
        ('pdf', 'PDF'),
        ('audio', 'Аудио'),
        ('doc', 'Документ'),
        ('image', 'Изображение'),
        ('video', 'Видео'),
        ('other', 'Другое'),
    )
    
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='attachments', verbose_name='Юнит')
    file_type = models.CharField(max_length=10, choices=FILE_TYPES, verbose_name='Тип файла')
    title = models.CharField(max_length=200, verbose_name='Название файла')
    file = models.FileField(upload_to='unit_attachments/', verbose_name='Файл')
    description = models.CharField(max_length=500, blank=True, verbose_name='Описание файла')
    file_size = models.CharField(max_length=50, blank=True, verbose_name='Размер файла')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Прикрепленный файл юнита'
        verbose_name_plural = 'Прикрепленные файлы юнитов'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.unit.title} - {self.title}"


class Topic(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='topics', verbose_name='Юнит')
    title = models.CharField(max_length=200, verbose_name='Название темы')
    theory_content = models.TextField(blank=True, verbose_name='Теоретическая часть')
    practice_content = models.TextField(blank=True, verbose_name='Практическая часть')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Тема'
        verbose_name_plural = 'Темы'
        ordering = ['order']

    def __str__(self):
        return f"{self.unit.title} - {self.title}"


class ModuleCardModule(models.Model):
    """Связь между учебным модулем и модулями карточек"""
    study_module = models.ForeignKey(StudyModule, on_delete=models.CASCADE, related_name='attached_card_modules', verbose_name='Учебный модуль')
    card_module = models.ForeignKey('cards.Module', on_delete=models.CASCADE, related_name='attached_to_study_modules', verbose_name='Модуль карточек')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Прикрепленный модуль карточек'
        verbose_name_plural = 'Прикрепленные модули карточек'
        ordering = ['order']
        unique_together = ('study_module', 'card_module')
    
    def __str__(self):
        return f"{self.study_module.title} - {self.card_module.name}"


class GrammarTask(models.Model):
    """Задания для грамматической практики"""
    TASK_TYPES = (
        ('matching', 'Соединение слов'),
        ('sentence_rewrite', 'Переписывание предложений'),
        ('translation_choice', 'Выбор перевода'),
        ('sentence_builder', 'Составление предложений'),
    )
    
    skill = models.ForeignKey(UnitSkill, on_delete=models.CASCADE, related_name='grammar_tasks', verbose_name='Навык')
    task_type = models.CharField(max_length=20, choices=TASK_TYPES, verbose_name='Тип задания')
    title = models.CharField(max_length=200, verbose_name='Название задания')
    description = models.TextField(verbose_name='Описание задания')
    instruction = models.TextField(verbose_name='Инструкция')
    content = models.JSONField(verbose_name='Содержание задания')
    correct_answer = models.JSONField(verbose_name='Правильный ответ')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    
    class Meta:
        verbose_name = 'Задание грамматики'
        verbose_name_plural = 'Задания грамматики'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.skill.title} - {self.title}"


class UserTaskProgress(models.Model):
    """Прогресс пользователя по заданиям"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    task = models.ForeignKey(GrammarTask, on_delete=models.CASCADE, verbose_name='Задание')
    is_completed = models.BooleanField(default=False, verbose_name='Завершено')
    attempts = models.PositiveIntegerField(default=0, verbose_name='Попыток')
    correct_attempts = models.PositiveIntegerField(default=0, verbose_name='Правильных попыток')
    last_attempt = models.DateTimeField(auto_now=True, verbose_name='Последняя попытка')
    best_score = models.FloatField(default=0.0, verbose_name='Лучший результат')
    
    class Meta:
        verbose_name = 'Прогресс по заданию'
        verbose_name_plural = 'Прогресс по заданиям'
        unique_together = ('user', 'task')
    
    def __str__(self):
        return f"{self.user.username} - {self.task.title}"


class ModuleAccessRequest(models.Model):
    """Заявки пользователей на доступ к закрытым модулям"""
    REQUEST_STATUS = (
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрена'),
        ('rejected', 'Отклонена'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='module_access_requests',
        verbose_name='Пользователь'
    )
    module = models.ForeignKey(
        StudyModule,
        on_delete=models.CASCADE,
        related_name='access_requests',
        verbose_name='Модуль'
    )
    status = models.CharField(
        max_length=20,
        choices=REQUEST_STATUS,
        default='pending',
        verbose_name='Статус заявки'
    )
    message = models.TextField(
        blank=True,
        verbose_name='Сообщение от пользователя',
        help_text='Описание почему нужен доступ'
    )
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата подачи заявки')
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата рассмотрения')
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_access_requests',
        verbose_name='Рассмотревший'
    )
    reviewer_message = models.TextField(
        blank=True,
        verbose_name='Комментарий рассмотревшего'
    )
    
    class Meta:
        verbose_name = 'Заявка на доступ к модулю'
        verbose_name_plural = 'Заявки на доступ к модулям'
        ordering = ['-requested_at']
        unique_together = ('user', 'module')
    
    def __str__(self):
        return f"{self.user.username} - {self.module.title} ({self.get_status_display()})"


class UserModuleAccess(models.Model):
    """Отслеживание доступов пользователей к закрытым модулям"""
    ACCESS_TYPES = (
        ('request', 'Через заявку'),
        ('password', 'Через пароль'),
        ('author', 'Автор модуля'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='module_accesses',
        verbose_name='Пользователь'
    )
    module = models.ForeignKey(
        StudyModule,
        on_delete=models.CASCADE,
        related_name='user_accesses',
        verbose_name='Модуль'
    )
    access_type = models.CharField(
        max_length=20,
        choices=ACCESS_TYPES,
        verbose_name='Тип доступа'
    )
    granted_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата получения доступа')
    
    class Meta:
        verbose_name = 'Доступ пользователя к модулю'
        verbose_name_plural = 'Доступы пользователей к модулям'
        ordering = ['-granted_at']
        unique_together = ('user', 'module')
    
    def __str__(self):
        return f"{self.user.username} - {self.module.title} ({self.get_access_type_display()})"
