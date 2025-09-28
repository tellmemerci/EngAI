from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('cards', '0007_fix_bubble_game_duplicates'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='bubblegamerecord',
            unique_together={('user', 'module')},
        ),
    ] 