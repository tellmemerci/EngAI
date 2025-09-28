from django.db import migrations
from django.db.models import Count, Max

def remove_duplicates(apps, schema_editor):
    BubbleGameRecord = apps.get_model('cards', 'BubbleGameRecord')
    
    # Находим все дубликаты
    duplicates = (
        BubbleGameRecord.objects
        .values('user_id', 'module_id')
        .annotate(count=Count('id'))
        .filter(count__gt=1)
    )
    
    # Для каждой группы дубликатов
    for duplicate in duplicates:
        # Получаем все записи для данной пары user-module
        records = (
            BubbleGameRecord.objects
            .filter(
                user_id=duplicate['user_id'],
                module_id=duplicate['module_id']
            )
            .order_by('-score', '-created_at')  # Сортируем по score (по убыванию) и дате создания
        )
        
        # Оставляем только запись с максимальным score
        best_record = records.first()
        if best_record:
            # Удаляем все остальные записи
            records.exclude(id=best_record.id).delete()

def reverse_func(apps, schema_editor):
    # Обратная операция не требуется
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('cards', '0006_balloongamerecord_alter_bubblegamerecord_options_and_more'),
    ]

    operations = [
        migrations.RunPython(remove_duplicates, reverse_func),
    ] 