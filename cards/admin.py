from django.contrib import admin
from .models import Folder, Module, Card, LearningProgress, BubbleGameRecord, BalloonGameRecord

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'parent', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('name', 'user__username')

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'folder', 'module_type', 'created_at')
    list_filter = ('user', 'module_type', 'created_at')
    search_fields = ('name', 'user__username')

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('term', 'translation', 'module', 'created_at')
    list_filter = ('module', 'created_at')
    search_fields = ('term', 'translation', 'module__name')

@admin.register(BubbleGameRecord)
class BubbleGameRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'score', 'created_at')
    list_filter = ('user', 'module', 'created_at')
    search_fields = ('user__username', 'user__email', 'module__name')
    ordering = ('-score',)

@admin.register(LearningProgress)
class LearningProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'card', 'module', 'correct_attempts', 'incorrect_attempts', 'last_attempt', 'needs_review')
    list_filter = ('user', 'needs_review')
    search_fields = ('user__username', 'card__term', 'module__name')
    ordering = ('-last_attempt',)

@admin.register(BalloonGameRecord)
class BalloonGameRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'score', 'created_at', 'updated_at')
    list_filter = ('user', 'module', 'created_at')
    search_fields = ('user__username', 'user__email', 'module__name')
    ordering = ('-score',)

