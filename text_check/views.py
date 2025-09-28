from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import TextCheck, Error, Theme
import json
from django.utils import timezone
from datetime import timedelta

@login_required
def text_check_view(request):
    return render(request, 'text_check/text_check.html')

@login_required
def text_check_history(request):
    if request.method == 'GET':
        month_ago = timezone.now() - timedelta(days=31)
        history = TextCheck.objects.filter(user=request.user, created_at__gte=month_ago).order_by('-created_at')
        data = []
        
        for item in history:
            errors = Error.objects.filter(text_check=item).values('error_text', 'correction', 'error_type')
            themes = Theme.objects.filter(text_check=item).values('name', 'description')
            
            data.append({
                'original_text': item.original_text,
                'corrected_text': item.corrected_text,
                'created_at': item.created_at.strftime('%d.%m.%Y %H:%M'),
                'errors': list(errors),
                'themes': list(themes)
            })
            
        return JsonResponse({'status': 'success', 'history': data})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@login_required
def check_text(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            
            # TODO: Здесь будет интеграция с API для проверки текста
            # Временный пример ответа
            text_check = TextCheck.objects.create(
                user=request.user,
                original_text=text,
                corrected_text=text  # Временно оставляем текст без изменений
            )
            
            # Пример ошибок (в реальном приложении будут приходить от API)
            errors = [
                {
                    'text': 'grammar',
                    'correction': 'grammar',
                    'type': 'Spelling',
                    'position': 10
                }
            ]
            
            # Создаем записи об ошибках
            for error in errors:
                Error.objects.create(
                    text_check=text_check,
                    error_text=error['text'],
                    correction=error['correction'],
                    error_type=error['type'],
                    position=error['position']
                )
            
            # Пример тем для повторения
            themes = [
                {
                    'name': 'Present Simple',
                    'description': 'Basic tense for regular actions'
                }
            ]
            
            return JsonResponse({
                'status': 'success',
                'original_text': text,
                'corrected_text': text,
                'errors': errors,
                'themes': themes
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Only POST method is allowed'
    }, status=405)
