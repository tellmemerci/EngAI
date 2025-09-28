from django.contrib.auth.models import User
from django.http import HttpRequest
from .models import UserLog
import random
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def log_user_action(
    user: User,
    action: str,
    request: HttpRequest = None,
    details: dict = None
) -> UserLog:
    """
    Создает запись в логах о действии пользователя
    
    Args:
        user: Пользователь, совершивший действие
        action: Тип действия (должен соответствовать ACTION_CHOICES в модели UserLog)
        request: Объект запроса Django (опционально)
        details: Дополнительные детали действия (опционально)
    
    Returns:
        UserLog: Созданная запись в логах
    """
    log_data = {
        'user': user,
        'action': action,
    }
    
    if request:
        log_data['ip_address'] = request.META.get('REMOTE_ADDR')
        log_data['user_agent'] = request.META.get('HTTP_USER_AGENT')
    
    if details:
        log_data['details'] = details
    
    return UserLog.objects.create(**log_data)

def generate_sms_code(length=6):
    """
    Генерирует случайный SMS-код указанной длины.
    
    :param length: Длина кода (по умолчанию 6)
    :return: Строка с кодом
    """
    return ''.join(random.choices('0123456789', k=length))

def send_sms_code(phone_number, code):
    """
    Отправляет SMS-код на указанный номер телефона.
    
    В реальном приложении здесь будет интеграция с SMS-провайдером.
    Сейчас просто логируем код для демонстрации.
    
    :param phone_number: Номер телефона получателя
    :param code: SMS-код для отправки
    """
    try:
        # Здесь должна быть реальная логика отправки SMS
        # Например, через Twilio, Nexmo или другой SMS-сервис
        logger.info(f"SMS код {code} отправлен на номер {phone_number}")
        
        # Заглушка для демонстрации
        if settings.DEBUG:
            print(f"[DEBUG] SMS код: {code}")
    except Exception as e:
        logger.error(f"Ошибка отправки SMS: {e}")
        raise 