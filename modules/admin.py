from django.contrib import admin
from django.utils.html import format_html
from .models import Module, TaskBlock, Task, TaskOption


class TaskOptionInline(admin.TabularInline):
    model = TaskOption
    extra = 1
    min_num = 0
    verbose_name = 'Вариант ответа'
    verbose_name_plural = 'Варианты ответа'
    fields = ('text', 'is_correct', 'image_preview', 'audio_preview', 'image', 'audio')
    readonly_fields = ('image_preview', 'audio_preview')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" style="object-fit: contain;" />', obj.image.url)
        return "—"

    def audio_preview(self, obj):
        if obj.audio:
            return format_html('<audio controls src="{}" style="width: 150px;"></audio>', obj.audio.url)
        return "—"


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'status', 'image_preview', 'description_module')
    readonly_fields = ('image_preview',)
    list_filter = ('level', 'status')
    search_fields = ('name', 'description_module')

    fieldsets = (
        (None, {
            'fields': ('name', 'description_module', 'level', 'status', 'password_status')
        }),
        ('Изображение', {
            'fields': ('photo', 'image_preview'),
        }),
    )

    def image_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="100" height="60" style="object-fit: cover; border-radius: 4px;" />',
                obj.photo.url
            )
        return "Нет изображения"

    image_preview.short_description = 'Превью изображения'


@admin.register(TaskBlock)
class TaskBlockAdmin(admin.ModelAdmin):
    list_display = ('module', 'type')
    list_filter = ('type',)
    search_fields = ('module__name',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'task_block', 'task_type', 'short_prompt', 'short_description',
        'correct_answer', 'image_preview', 'audio_preview'
    )
    search_fields = ('description', 'prompt', 'correct_answer')
    list_filter = ('task_type', 'task_block__type')
    readonly_fields = ('image_preview', 'audio_preview')
    inlines = [TaskOptionInline]

    fieldsets = (
        (None, {
            'fields': ('task_block', 'task_type', 'prompt', 'description', 'correct_answer')
        }),
        ('Мультимедиа', {
            'fields': ('media_image', 'image_preview', 'media_audio', 'audio_preview')
        }),
    )

    def short_prompt(self, obj):
        return (obj.prompt[:50] + '...') if obj.prompt and len(obj.prompt) > 50 else obj.prompt
    short_prompt.short_description = 'Условие'

    def short_description(self, obj):
        return (obj.description[:75] + '...') if obj.description and len(obj.description) > 75 else obj.description
    short_description.short_description = 'Инструкция'

    def image_preview(self, obj):
        if obj.media_image:
            return format_html('<img src="{}" width="100" style="object-fit: contain;" />', obj.media_image.url)
        return "—"
    image_preview.short_description = 'Изображение'

    def audio_preview(self, obj):
        if obj.media_audio:
            return format_html('<audio controls src="{}" style="width: 200px;"></audio>', obj.media_audio.url)
        return "—"
    audio_preview.short_description = 'Аудио'


@admin.register(TaskOption)
class TaskOptionAdmin(admin.ModelAdmin):
    list_display = ('task', 'text', 'is_correct', 'image_preview', 'audio_preview')
    list_filter = ('is_correct',)
    search_fields = ('text',)
    readonly_fields = ('image_preview', 'audio_preview')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" style="object-fit: contain;" />', obj.image.url)
        return "—"
    image_preview.short_description = 'Изобр.'

    def audio_preview(self, obj):
        if obj.audio:
            return format_html('<audio controls src="{}" style="width: 150px;"></audio>', obj.audio.url)
        return "—"
    audio_preview.short_description = 'Аудио'
