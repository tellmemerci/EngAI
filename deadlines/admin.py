from django.contrib import admin
from .models import Deadline

@admin.register(Deadline)
class DeadlineAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'date', 'time', 'priority', 'is_completed', 'is_overdue']
    list_filter = ['priority', 'is_completed', 'date', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    list_editable = ['is_completed']
    date_hierarchy = 'date'
    ordering = ['date', 'time']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'title', 'description')
        }),
        ('Дата и время', {
            'fields': ('date', 'time')
        }),
        ('Настройки', {
            'fields': ('priority', 'color', 'is_completed')
        }),
    )
    
    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Просрочен'
