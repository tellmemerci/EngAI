from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cards', '0008_add_unique_constraint'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='saved_by_users',
            field=models.ManyToManyField(
                related_name='saved_modules',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Пользователи, сохранившие модуль',
                blank=True
            ),
        ),
        # Удаляем старое поле is_saved, так как оно больше не нужно
        migrations.RemoveField(
            model_name='module',
            name='is_saved',
        ),
    ] 