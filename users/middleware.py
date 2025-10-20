from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser


class ProfileCompletionMiddleware:
    """
    Middleware для проверки заполненности профиля пользователя
    Перенаправляет на страницу завершения профиля, если профиль не завершен
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Список URL которые не требуют завершенного профиля
        self.excluded_paths = [
            '/complete-profile/',
            '/logout/',
            '/login/',
            '/register/',
            '/admin/',
            '/privacy-policy/',
            '/static/',
            '/media/',
            '/complete/',  # OAuth callback URLs
            '/disconnect/',
            '/associate/',
        ]

    def __call__(self, request):
        # Проверяем только для авторизованных пользователей
        if not isinstance(request.user, AnonymousUser) and request.user.is_authenticated:
            # Проверяем, не находимся ли мы на исключенной странице
            current_path = request.path
            excluded = any(current_path.startswith(path) for path in self.excluded_paths)
            
            if not excluded and not request.user.is_profile_complete():
                # Если профиль не завершен и мы не на исключенной странице,
                # перенаправляем на завершение профиля
                return redirect('complete_profile')
        
        response = self.get_response(request)
        return response