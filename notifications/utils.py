from .models import Notification

def create_notification(user, title, text, notification_type='info', image=None):
    """
    Создает новое уведомление для пользователя.
    
    Args:
        user: Пользователь, которому предназначено уведомление
        title (str): Заголовок уведомления
        text (str): Текст уведомления
        notification_type (str): Тип уведомления (info, success, warning, error, achievement, message, update)
        image (File, optional): Изображение для уведомления
    
    Returns:
        Notification: Созданное уведомление
    """
    return Notification.objects.create(
        user=user,
        title=title,
        text=text,
        notification_type=notification_type,
        image=image
    )

def create_achievement_notification(user, achievement_title, achievement_text):
    """
    Создает уведомление о достижении.
    
    Args:
        user: Пользователь, получивший достижение
        achievement_title (str): Название достижения
        achievement_text (str): Описание достижения
    
    Returns:
        Notification: Созданное уведомление о достижении
    """
    return create_notification(
        user=user,
        title=f"Новое достижение: {achievement_title}",
        text=achievement_text,
        notification_type='achievement'
    )

def create_lesson_complete_notification(user, lesson_title):
    """
    Создает уведомление о завершении урока.
    
    Args:
        user: Пользователь, завершивший урок
        lesson_title (str): Название урока
    
    Returns:
        Notification: Созданное уведомление
    """
    return create_notification(
        user=user,
        title="Урок завершен",
        text=f"Поздравляем! Вы успешно завершили урок '{lesson_title}'",
        notification_type='success'
    )

def create_streak_notification(user, days):
    """
    Создает уведомление о достижении серии дней обучения.
    
    Args:
        user: Пользователь
        days (int): Количество дней подряд
    
    Returns:
        Notification: Созданное уведомление
    """
    return create_notification(
        user=user,
        title=f"Серия {days} дней!",
        text=f"Вы занимаетесь уже {days} дней подряд. Продолжайте в том же духе!",
        notification_type='achievement'
    )

def create_vocabulary_milestone_notification(user, words_count):
    """
    Создает уведомление о достижении определенного количества слов в словаре.
    
    Args:
        user: Пользователь
        words_count (int): Количество слов
    
    Returns:
        Notification: Созданное уведомление
    """
    return create_notification(
        user=user,
        title=f"Словарный запас {words_count}+",
        text=f"Поздравляем! Ваш словарный запас достиг {words_count} слов!",
        notification_type='achievement'
    ) 