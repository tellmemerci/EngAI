from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import UserWord
import json
import logging
from gtts import gTTS
import tempfile
import os

logger = logging.getLogger(__name__)

# Create your views here.

@login_required
def dictionary_view(request):
    return render(request, 'dictionary/dictionary.html')

@login_required
@require_http_methods(["GET"])
def saved_words(request):
    logger.info(f"Fetching saved words for user: {request.user.email}")
    words = UserWord.objects.filter(user=request.user, is_saved=True).order_by('-updated_at')
    logger.info(f"Found {words.count()} saved words for user {request.user.email}")
    return JsonResponse({
        'words': [{
            'word': word.word,
            'translation': word.translation,
            'usage_count': word.usage_count
        } for word in words]
    })

@login_required
@require_http_methods(["GET"])
def frequent_words(request):
    words = UserWord.objects.filter(user=request.user).order_by('-usage_count')[:50]
    return JsonResponse({
        'words': [{
            'word': word.word,
            'translation': word.translation,
            'usage_count': word.usage_count
        } for word in words]
    })

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def save_word(request):
    try:
        data = json.loads(request.body)
        word = data.get('word')
        translation = data.get('translation')
        
        if not word or not translation:
            return JsonResponse({'error': 'Missing word or translation'}, status=400)
        
        logger.info(f"Saving word: {word} for user: {request.user.email}")
        
        # Проверяем существующие слова пользователя
        existing_words = UserWord.objects.filter(user=request.user).count()
        logger.info(f"User {request.user.email} has {existing_words} total words")
        
        user_word, created = UserWord.objects.get_or_create(
            user=request.user,
            word=word,
            defaults={'translation': translation, 'is_saved': True}
        )
        
        if not created:
            user_word.is_saved = True
            user_word.save()
            logger.info(f"Updated existing word: {word} for user {request.user.email}")
        else:
            logger.info(f"Created new word: {word} for user {request.user.email}")
        
        # Проверяем количество сохраненных слов после операции
        saved_words_count = UserWord.objects.filter(user=request.user, is_saved=True).count()
        logger.info(f"User {request.user.email} now has {saved_words_count} saved words")
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Error saving word: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def delete_word(request):
    try:
        data = json.loads(request.body)
        word = data.get('word')
        
        if not word:
            return JsonResponse({'error': 'Missing word'}, status=400)
        
        logger.info(f"Deleting word: {word} for user: {request.user.email}")
        
        user_word = UserWord.objects.filter(user=request.user, word=word).first()
        if user_word:
            user_word.is_saved = False
            user_word.save()
            logger.info(f"Word deleted successfully: {word}")
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'error': 'Word not found'}, status=404)
    except Exception as e:
        logger.error(f"Error deleting word: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def text_to_speech(request):
    temp_file = None
    try:
        word = request.GET.get('word')
        if not word:
            return JsonResponse({'error': 'Word parameter is required'}, status=400)
        
        # Создаем временный файл для сохранения аудио
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        temp_file.close()  # Закрываем файл перед использованием gTTS
        
        # Генерируем аудио файл
        tts = gTTS(text=word, lang='en', slow=False)
        tts.save(temp_file.name)
        
        # Читаем файл и отправляем его как ответ
        with open(temp_file.name, 'rb') as audio_file:
            response = HttpResponse(audio_file.read(), content_type='audio/mpeg')
            response['Content-Disposition'] = f'attachment; filename="{word}.mp3"'
        
        return response
            
    except Exception as e:
        logger.error(f"Error in text_to_speech: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        # Удаляем временный файл в блоке finally
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except Exception as e:
                logger.error(f"Error deleting temporary file: {str(e)}")
