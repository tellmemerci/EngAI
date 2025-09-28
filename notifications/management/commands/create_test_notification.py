from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates a test notification for the first user in the database'

    def handle(self, *args, **kwargs):
        try:
            user = User.objects.first()
            if user:
                notification = Notification.objects.create(
                    user=user,
                    title='Тестовое уведомление',
                    text='Это тестовое уведомление для проверки системы уведомлений.'
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created test notification for user {user.username}'))
            else:
                self.stdout.write(self.style.ERROR('No users found in the database'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating test notification: {str(e)}')) 