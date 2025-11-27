from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserLog, PromoCode, Subscription, Payment

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональные данные', {'fields': ('first_name', 'last_name', 'birth_date', 'phone_number', 'city')}),
        ('Уровни языка', {'fields': ('current_language_level', 'desired_language_level')}),
        ('Права', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

@admin.register(UserLog)
class UserLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__email', 'ip_address')
    readonly_fields = ('user', 'action', 'timestamp', 'ip_address', 'user_agent', 'details')


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'is_active', 'valid_from', 'valid_until', 'used_count', 'usage_limit')
    list_filter = ('is_active', 'valid_from', 'valid_until')
    search_fields = ('code',)
    readonly_fields = ('used_count', 'created_at')
    fieldsets = (
        (None, {
            'fields': ('code', 'discount_percent', 'is_active')
        }),
        ('Временные рамки', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Лимиты', {
            'fields': ('usage_limit', 'used_count')
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_type', 'is_active', 'start_date', 'end_date', 'auto_renewal')
    list_filter = ('subscription_type', 'is_active', 'auto_renewal', 'start_date')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('start_date', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'subscription_type', 'is_active')
        }),
        ('Период действия', {
            'fields': ('end_date', 'auto_renewal')
        }),
        ('Промокод', {
            'fields': ('promo_code',)
        }),
        ('Системная информация', {
            'fields': ('start_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'currency', 'status', 'subscription', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('user__email', 'yookassa_payment_id')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'subscription', 'amount', 'currency', 'status')
        }),
        ('ЮKassa', {
            'fields': ('yookassa_payment_id', 'payment_url')
        }),
        ('Скидки', {
            'fields': ('promo_code', 'discount_amount')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


admin.site.register(User, CustomUserAdmin)