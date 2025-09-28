from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates test notifications of different types for the first user'

    def handle(self, *args, **kwargs):
        try:
            user = User.objects.first()
            if user:
                notifications = [
                    {
                        'title': 'Добро пожаловать!',
                        'text': 'Добро пожаловать в нашу платформу для изучения английского языка.',
                        'notification_type': 'info'
                    },
                    {
                        'title': 'Урок завершен',
                        'text': 'Поздравляем! Вы успешно завершили урок "Времена в английском языке".',
                        'notification_type': 'success'
                    },
                    {
                        'title': 'Напоминание',
                        'text': 'Не забудьте выполнить домашнее задание до завтра.',
                        'notification_type': 'warning'
                    },
                    {
                        'title': 'Ошибка синхронизации',
                        'text': 'Произошла ошибка при синхронизации вашего прогресса. Мы уже работаем над исправлением.',
                        'notification_type': 'error'
                    },
                    {
                        'title': 'Новое достижение!',
                        'text': 'Вы получили достижение "Словарный запас 500+" за изучение более 500 слов!',
                        'notification_type': 'achievement'
                    },
                    {
                        'title': 'Новое сообщение',
                        'text': 'У вас новое сообщение от преподавателя.',
                        'notification_type': 'message'
                    },
                    {
                        'title': 'Обновление платформы',
                        'text': 'Мы добавили новые функции и улучшили производительность платформы.',
                        'notification_type': 'update'
                    }
                ]

                for notif_data in notifications:
                    Notification.objects.create(
                        user=user,
                        **notif_data
                    )
                
                self.stdout.write(self.style.SUCCESS(f'Successfully created {len(notifications)} test notifications'))
            else:
                self.stdout.write(self.style.ERROR('No users found in the database'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating test notifications: {str(e)}')) 