from django.contrib import admin
from django.utils.html import format_html
from .models import StudyModule, ModuleSection, ModuleSkill, TheoryCard, ModuleAttachment, Unit, Topic, ModuleCardModule, UnitSection, UnitSkill, UnitTheoryCard, UnitAttachment, GrammarTask, UserTaskProgress

@admin.register(StudyModule)
class StudyModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'module_type', 'is_published', 'created_at', 'display_image', 'saved_count')
    list_filter = ('module_type', 'is_published', 'created_at')
    search_fields = ('title', 'description', 'author__username')
    readonly_fields = ('created_at', 'updated_at', 'saved_count')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'image')
        }),
        ('Настройки публикации', {
            'fields': ('author', 'module_type', 'is_published')
        }),
        ('Дополнительная информация', {
            'fields': ('created_at', 'updated_at', 'saved_count'),
            'classes': ('collapse',)
        }),
    )

    def saved_count(self, obj):
        """Возвращает количество пользователей, сохранивших модуль"""
        return obj.saved_by.count()
    saved_count.short_description = 'Сохранений'

    def display_image(self, obj):
        """Отображает миниатюру изображения в списке"""
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return "Нет изображения"
    display_image.short_description = 'Изображение'

    def get_queryset(self, request):
        """Оптимизация запросов для уменьшения нагрузки на БД"""
        return super().get_queryset(request).prefetch_related('saved_by').select_related('author')

    def save_model(self, request, obj, form, change):
        """Автоматически устанавливает текущего пользователя как автора при создании"""
        if not change:  # Если это новый объект
            obj.author = request.user
        super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ('admin/css/study_modules.css',)
        }


class TheoryCardInline(admin.TabularInline):
    model = TheoryCard
    extra = 1
    fields = ('title', 'content', 'order')


@admin.register(ModuleSection)
class ModuleSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'section_type', 'order')
    list_filter = ('section_type', 'module')
    search_fields = ('title', 'module__title')
    ordering = ('module', 'order')
    inlines = [TheoryCardInline]


@admin.register(ModuleSkill)
class ModuleSkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'skill_type', 'is_available', 'order')
    list_filter = ('skill_type', 'is_available', 'module')
    search_fields = ('title', 'module__title')
    ordering = ('module', 'order')
    list_editable = ('is_available', 'order')


@admin.register(TheoryCard)
class TheoryCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'order')
    list_filter = ('section__module', 'section')
    search_fields = ('title', 'content')
    ordering = ('section', 'order')


@admin.register(ModuleAttachment)
class ModuleAttachmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'file_type', 'file_size', 'order')
    list_filter = ('file_type', 'module')
    search_fields = ('title', 'module__title')
    ordering = ('module', 'order')


class TopicInline(admin.TabularInline):
    model = Topic
    extra = 1
    fields = ('title', 'theory_content', 'practice_content', 'order')
    classes = ('collapse',)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order', 'display_image')
    list_filter = ('module',)
    search_fields = ('title', 'module__title')
    ordering = ('module', 'order')
    inlines = [TopicInline]
    
    def display_image(self, obj):
        """Отображает миниатюру изображения юнита"""
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return "Нет изображения"
    display_image.short_description = 'Изображение'


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit', 'order', 'has_theory', 'has_practice')
    list_filter = ('unit__module', 'unit')
    search_fields = ('title', 'theory_content', 'practice_content')
    ordering = ('unit', 'order')
    
    def has_theory(self, obj):
        """Показывает, есть ли теоретическая часть"""
        return bool(obj.theory_content)
    has_theory.boolean = True
    has_theory.short_description = 'Есть теория'
    
    def has_practice(self, obj):
        """Показывает, есть ли практическая часть"""
        return bool(obj.practice_content)
    has_practice.boolean = True
    has_practice.short_description = 'Есть практика'


@admin.register(ModuleCardModule)
class ModuleCardModuleAdmin(admin.ModelAdmin):
    list_display = ('study_module', 'card_module', 'order')
    list_filter = ('study_module', 'card_module__user')
    search_fields = ('study_module__title', 'card_module__name')
    ordering = ('study_module', 'order')


# Админка для моделей юнитов
class UnitTheoryCardInline(admin.TabularInline):
    model = UnitTheoryCard
    extra = 1
    fields = ('title', 'content', 'order')


@admin.register(UnitSection)
class UnitSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit', 'section_type', 'order')
    list_filter = ('section_type', 'unit__module')
    search_fields = ('title', 'unit__title')
    ordering = ('unit', 'order')
    inlines = [UnitTheoryCardInline]


@admin.register(UnitSkill)
class UnitSkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit', 'skill_type', 'is_available', 'order')
    list_filter = ('skill_type', 'is_available', 'unit__module')
    search_fields = ('title', 'unit__title')
    ordering = ('unit', 'order')
    list_editable = ('is_available', 'order')


@admin.register(UnitTheoryCard)
class UnitTheoryCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'order')
    list_filter = ('section__unit__module', 'section')
    search_fields = ('title', 'content')
    ordering = ('section', 'order')


@admin.register(UnitAttachment)
class UnitAttachmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit', 'file_type', 'file_size', 'order')
    list_filter = ('file_type', 'unit__module')
    search_fields = ('title', 'unit__title')
    ordering = ('unit', 'order')


@admin.register(GrammarTask)
class GrammarTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'skill', 'task_type', 'is_active', 'order')
    list_filter = ('task_type', 'is_active', 'skill__unit__module')
    search_fields = ('title', 'description', 'skill__title')
    ordering = ('skill', 'order')
    readonly_fields = ('skill',)


@admin.register(UserTaskProgress)
class UserTaskProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'is_completed', 'attempts', 'correct_attempts', 'best_score', 'last_attempt')
    list_filter = ('is_completed', 'task__task_type', 'task__skill__unit__module')
    search_fields = ('user__username', 'task__title')
    ordering = ('-last_attempt',)
    readonly_fields = ('last_attempt',)
