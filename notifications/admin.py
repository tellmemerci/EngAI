from django.contrib import admin
from django.utils.html import format_html
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'user',
        'notification_type',
        'colored_type',
        'icon_preview',
        'created_at',
        'is_read'
    )
    list_filter = (
        'notification_type',
        'is_read',
        'created_at',
    )
    search_fields = (
        'title',
        'text',
        'user__username'
    )
    list_editable = ('is_read',)
    readonly_fields = (
        'created_at',
        'icon_preview',
        'color_preview'
    )
    fieldsets = (
        (None, {
            'fields': (
                'title',
                'text',
                'user',
                'notification_type'
            )
        }),
        ('Дополнительные данные', {
            'fields': (
                'image',
                'is_read',
                'created_at',
                'icon_preview',
                'color_preview'
            ),
        }),
    )
    actions = ['mark_as_read', 'mark_as_unread']

    @admin.display(description='Цвет')
    def colored_type(self, obj):
        return format_html(
            '<span style="color: {};">{}</span>',
            obj.color,
            obj.get_notification_type_display()
        )

    @admin.display(description='Иконка')
    def icon_preview(self, obj):
        return format_html(
            '<i class="bi {}"></i> {}',
            obj.icon_class,
            obj.icon_class
        )

    @admin.display(description='Цвет')
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}"></div> {}',
            obj.color,
            obj.color
        )

    @admin.action(description='Пометить как прочитанные')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description='Пометить как непрочитанные')
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)