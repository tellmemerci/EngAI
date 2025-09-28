from django.db import models
from study_modules.models import Topic # Импортируем модель Topic


class Module(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название модуля')
    description_module = models.CharField(max_length=500, verbose_name='Описание модуля')
    photo = models.ImageField(upload_to='modules_photo/', null=True, blank=True, verbose_name='Фото модуля')
    status = models.CharField(max_length=25, choices=(
        ('Публичный доступ', 'Публичный доступ'),
        ('Частный доступ', 'Частный доступ')
    ), default='Публичный доступ', verbose_name='Статус публичности')
    password_status = models.CharField(max_length=10, verbose_name='Пароль для частного доступа', default=None)
    level = models.CharField(max_length=10, choices=(
        ('A1', 'A1'),  ('A2', 'A2'),  ('B1', 'B1'),  ('B2', 'B2'),  ('C1', 'C1'),  ('C2', 'C2'),
    ), default='B1', verbose_name='Уровень модуля')

    def __str__(self):
        return self.name


class TaskBlock(models.Model):
    TASK_TYPES = (
        ('Listening', 'Listening'),
        ('Writing', 'Writing'),
        ('Grammar', 'Grammar'),
        ('Reading', 'Reading'),
        ('Speaking', 'Speaking'),
        ('Words', 'Words'),
    )

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='task_blocks', verbose_name='Модуль')
    type = models.CharField(max_length=20, choices=TASK_TYPES, verbose_name='Тип блока')

    def __str__(self):
        return f"{self.module.name} - {self.type}"


class Task(models.Model):
    TASK_TYPES = (
        ('fill_in_the_blank', 'Заполнить пропуск'),
        ('match', 'Соединить элементы'),
        ('correct_sentence', 'Исправить предложение'),
        ('choose_correct', 'Выбрать правильный вариант'),
        ('rewrite', 'Переписать'),
        ('transform_verb', 'Изменить глагол'),
        ('other', 'Другое'),
    )

    task_block = models.ForeignKey(TaskBlock, on_delete=models.CASCADE, related_name='tasks', verbose_name='Блок заданий')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True, verbose_name='Тема') # Добавляем внешний ключ к Topic
    task_type = models.CharField(max_length=30, choices=TASK_TYPES, default='other', verbose_name='Тип задания')
    prompt = models.TextField(verbose_name='Неправильное или условное предложение')
    description = models.TextField(verbose_name='Описание задания / инструкция')
    media_image = models.ImageField(upload_to='task_media/images/', null=True, blank=True, verbose_name='Изображение к заданию')
    media_audio = models.FileField(upload_to='task_media/audio/', null=True, blank=True, verbose_name='Аудио к заданию')
    correct_answer = models.CharField(max_length=255, verbose_name='Правильный ответ', blank=True, null=True)

    def __str__(self):
        return f"{self.get_task_type_display()} — {self.task_block.type}"


class TaskOption(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='options', verbose_name='Задание')
    text = models.CharField(max_length=255, verbose_name='Вариант ответа', null=True, blank=True)
    is_correct = models.BooleanField(default=False, verbose_name='Это правильный вариант?')
    image = models.ImageField(upload_to='option_media/images/', null=True, blank=True, verbose_name='Изображение варианта')
    audio = models.FileField(upload_to='option_media/audio/', null=True, blank=True, verbose_name='Аудио варианта')

    def __str__(self):
        display_text = self.text if self.text else 'Мультимедиа-вариант'
        return f"{display_text} ({'✔' if self.is_correct else '✘'})"
