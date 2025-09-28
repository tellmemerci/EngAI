from django.contrib import admin
from .models import UserWord

@admin.register(UserWord)
class UserWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'translation', 'user', 'usage_count', 'is_saved', 'created_at')
    list_filter = ('is_saved', 'created_at')
    search_fields = ('word', 'translation', 'user__email')
    ordering = ('-created_at',)
