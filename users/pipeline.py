from users.models import User


def create_user_profile(backend, user, response, *args, **kwargs):
    """
    Кастомная функция pipeline для создания профиля пользователя
    при регистрации через социальные сети
    """
    if user and not user.is_active:
        user.is_active = True
        user.save()
    
    # Заполняем дополнительные поля если они пустые
    if user:
        updated = False
        
        # Для Google
        if backend.name == 'google-oauth2':
            if not user.first_name and response.get('given_name'):
                user.first_name = response.get('given_name')
                updated = True
            if not user.last_name and response.get('family_name'):
                user.last_name = response.get('family_name')
                updated = True
                
        # Для GitHub
        elif backend.name == 'github':
            if not user.first_name and response.get('name'):
                # GitHub возвращает полное имя, разделим его
                name_parts = response.get('name', '').split(' ', 1)
                user.first_name = name_parts[0] if name_parts else ''
                if len(name_parts) > 1:
                    user.last_name = name_parts[1]
                updated = True
                
        # Для Apple
        elif backend.name == 'apple-id':
            if not user.first_name and response.get('name', {}).get('firstName'):
                user.first_name = response.get('name', {}).get('firstName')
                updated = True
            if not user.last_name and response.get('name', {}).get('lastName'):
                user.last_name = response.get('name', {}).get('lastName')
                updated = True
        
        # Устанавливаем значения по умолчанию для обязательных полей
        if not user.current_language_level:
            user.current_language_level = 'A1'  # Устанавливаем начальный уровень по умолчанию
            updated = True
            
        if not user.desired_language_level:
            user.desired_language_level = 'B1'  # Устанавливаем желаемый уровень по умолчанию
            updated = True
            
        if not user.city:
            user.city = 'Не указан'
            updated = True
            
        if not user.phone_number:
            user.phone_number = ''
            updated = True
        
        if updated:
            user.save()


def redirect_to_profile_completion(strategy, user, is_new=False, *args, **kwargs):
    """
    Перенаправляет новых пользователей на страницу завершения профиля
    """
    if user and not user.is_profile_complete():
        from django.shortcuts import reverse
        from social_core.pipeline.partial import partial
        
        # Используем redirect через strategy
        return strategy.redirect(reverse('complete_profile'))


def associate_by_email(backend, details, user=None, *args, **kwargs):
    """
    Связывает аккаунты по email адресу
    """
    email = details.get('email')
    if email:
        try:
            existing_user = User.objects.get(email=email)
            if user is None:
                return {'user': existing_user, 'is_new': False}
        except User.DoesNotExist:
            pass
    return None