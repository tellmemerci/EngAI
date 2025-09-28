from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from study_modules.models import StudyModule, ModuleSection, ModuleSkill, TheoryCard, ModuleAttachment

User = get_user_model()

class Command(BaseCommand):
    help = 'Создает тестовые данные для демонстрации модулей'

    def handle(self, *args, **options):
        # Удаляем старые данные
        StudyModule.objects.filter(title='Грамматика английского языка').delete()
        
        # Создаем пользователя, если его нет
        user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Создан тестовый пользователь'))

        # Создаем модуль
        module = StudyModule.objects.create(
            title='Грамматика английского языка',
            description='Комплексный курс по изучению грамматики английского языка для начинающих и продолжающих.',
            author=user,
            module_type='free',
            is_published=True
        )

        self.stdout.write(self.style.SUCCESS('Создан модуль: Грамматика английского языка'))

        # Создаем теоретическую секцию
        theory_section, created = ModuleSection.objects.get_or_create(
            module=module,
            section_type='theory',
            defaults={
                'title': '1. Теоретическая часть',
                'description': 'Теоретические основы английской грамматики',
                'order': 1
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS('Создана теоретическая секция'))

        # Создаем теоретические карточки
        theory_cards_data = [
            {
                'title': 'Основы грамматики',
                'content': 'Изучение базовых грамматических правил английского языка',
                'order': 1
            },
            {
                'title': 'Времена глаголов',
                'content': 'Подробное изучение всех времен английского языка',
                'order': 2
            }
        ]

        for card_data in theory_cards_data:
            card, created = TheoryCard.objects.get_or_create(
                section=theory_section,
                title=card_data['title'],
                defaults=card_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создана карточка: {card_data["title"]}'))

        # Создаем практическую секцию
        practice_section, created = ModuleSection.objects.get_or_create(
            module=module,
            section_type='practice',
            defaults={
                'title': '2. Практическая часть',
                'description': 'Практические упражнения и задания',
                'order': 2
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS('Создана практическая секция'))

        # Создаем практические навыки
        skills_data = [
            {
                'skill_type': 'listening',
                'title': '2.1 Listening',
                'description': 'Развитие навыков аудирования',
                'order': 1,
                'is_available': True
            },
            {
                'skill_type': 'writing',
                'title': '2.2 Writing',
                'description': 'Практика письменной речи',
                'order': 2,
                'is_available': True
            },
            {
                'skill_type': 'grammar',
                'title': '2.3 Grammar',
                'description': 'Изучение грамматических правил',
                'order': 3,
                'is_available': True
            },
            {
                'skill_type': 'reading',
                'title': '2.4 Reading',
                'description': 'Улучшение навыков чтения',
                'order': 4,
                'is_available': True
            },
            {
                'skill_type': 'speaking',
                'title': '2.5 Speaking',
                'description': 'Развитие устной речи',
                'order': 5,
                'is_available': True
            },
            {
                'skill_type': 'words',
                'title': '2.6 Words',
                'description': 'Расширение словарного запаса',
                'order': 6,
                'is_available': True
            },
            {
                'skill_type': 'watching',
                'title': '2.7 Watching',
                'description': 'Просмотр видео материалов',
                'order': 7,
                'is_available': False  # Заблокировано для демонстрации
            },
            {
                'skill_type': 'test',
                'title': '2.8 Test',
                'description': 'Проверка знаний',
                'order': 8,
                'is_available': True
            }
        ]

        for skill_data in skills_data:
            skill, created = ModuleSkill.objects.get_or_create(
                module=module,
                skill_type=skill_data['skill_type'],
                defaults=skill_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан навык: {skill_data["title"]}'))

        # Создаем прикрепленные файлы
        attachments_data = [
            {
                'file_type': 'pdf',
                'title': 'Грамматика.pdf',
                'description': 'Основной учебник по грамматике',
                'file_size': '2.4 MB · 15 страниц',
                'order': 1
            },
            {
                'file_type': 'audio',
                'title': 'Аудиоурок.mp3',
                'description': 'Аудиоматериалы для прослушивания',
                'file_size': '15.2 MB · 45 минут',
                'order': 2
            },
            {
                'file_type': 'doc',
                'title': 'Тексты.docx',
                'description': 'Текстовые материалы для чтения',
                'file_size': '3.1 MB · 10 документов',
                'order': 3
            }
        ]

        for attachment_data in attachments_data:
            # Создаем фиктивный файл для демонстрации
            attachment, created = ModuleAttachment.objects.get_or_create(
                module=module,
                title=attachment_data['title'],
                defaults={
                    **attachment_data,
                    'file': 'dummy_file.txt'  # В реальном приложении здесь будет настоящий файл
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан файл: {attachment_data["title"]}'))

        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы!'))
        self.stdout.write(f'Модуль доступен по адресу: /modules/{module.id}/detail/')
