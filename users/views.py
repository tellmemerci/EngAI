from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, PasswordChangeForm, ProfileEditForm
from .utils import log_user_action, generate_sms_code, send_sms_code
from django.core.exceptions import ValidationError
from .models import User, Friendship, Chat, Message, StudyGroup, StudyGroupMembership, GroupChat, GroupMessage
from django.core.mail import send_mail
import random
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.core.paginator import Paginator

def index_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'users/index.html')

def registration_view(request):
    if request.user.is_authenticated:
        return redirect('index')
        
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        
        # Проверка согласия на обработку персональных данных
        if not request.POST.get('personal_data_agreement'):
            messages.error(request, 'Необходимо согласиться с обработкой персональных данных')
            return render(request, 'users/registration.html', {'form': form})
        
        if form.is_valid():
            try:
                # Проверка уникальности email
                User = get_user_model()
                if User.objects.filter(email=form.cleaned_data['email']).exists():
                    messages.error(request, 'Пользователь с таким email уже существует')
                    return render(request, 'users/registration.html', {'form': form})
                
                # Создание пользователя
                user = form.save(commit=False)
                user.is_active = True  # Пользователь активен сразу
                user.save()
                
                # Авторизуем пользователя с указанием бэкенда
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                # Логируем действие
                log_user_action(user, 'register', request)
                
                messages.success(request, 'Регистрация успешно завершена!')
                return redirect('index')
            
            except ValidationError as e:
                messages.error(request, str(e))
                return render(request, 'users/registration.html', {'form': form})
    else:
        form = RegistrationForm()
    
    return render(request, 'users/registration.html', {'form': form})

def sms_verification_view(request):
    if request.method == 'POST':
        sms_code = request.session.get('registration_sms_code')
        user_id = request.session.get('registration_user_id')
        
        if not sms_code or not user_id:
            messages.error(request, 'Истекло время ожидания. Пройдите регистрацию заново.')
            return redirect('register')
        
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
            entered_code = request.POST.get('sms_code')
            
            if entered_code == sms_code:
                user.is_active = True
                user.save()
                
                # Очистка сессии
                del request.session['registration_sms_code']
                del request.session['registration_user_id']
                
                messages.success(request, 'Регистрация успешно завершена! Теперь вы можете войти.')
                return redirect('login')
            else:
                messages.error(request, 'Неверный код подтверждения')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь не найден')
    
    return render(request, 'users/sms_verification.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/home/')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            log_user_action(user, 'login', request)
            return redirect('/home/')
        else:
            messages.error(request, 'Неверный email или пароль')
    
    return render(request, 'users/login.html')

def logout_view(request):
    if request.user.is_authenticated:
        log_user_action(request.user, 'logout', request)
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            log_user_action(request.user, 'profile_update', request)
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
        # Не добавляем общее сообщение об ошибке, ошибки отображаются рядом с полями
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'users/profile.html', {'form': form})

def change_password_view(request):
    if request.user.is_authenticated:
        # Для авторизованных пользователей - изменение пароля
        if request.method == 'POST':
            form = PasswordChangeForm(request.POST)
            if form.is_valid():
                user = request.user
                user.set_password(form.cleaned_data['password1'])
                user.save()
                log_user_action(user, 'password_change', request)
                messages.success(request, 'Пароль успешно изменен!')
                return redirect('login')
        else:
            form = PasswordChangeForm()
        
        return render(request, 'users/change_password.html', {'form': form})
    else:
        # Для неавторизованных пользователей - сброс пароля по email
        if request.method == 'POST':
            email = request.POST.get('email')
            User = get_user_model()
            try:
                user = User.objects.get(email=email)
                # Здесь в реальном приложении отправлялся бы email со ссылкой для сброса
                log_user_action(user, 'password_reset', request)
                messages.success(request, 'Инструкции по сбросу пароля отправлены на ваш email.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'Пользователь с таким email не найден.')
        
        return render(request, 'users/password_reset.html')

def privacy_policy_view(request):
    return render(request, 'users/privacy_policy.html')


def complete_profile_view(request):
    """
    Представление для завершения профиля после OAuth регистрации
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Если профиль уже заполнен, перенаправляем на главную
    if request.user.is_profile_complete():
        # Обновляем флаг завершенности профиля
        request.user.profile_completed = True
        request.user.save()
        return redirect('home')
    
    # Определяем провайдера аутентификации
    provider_name = 'социальную сеть'
    
    # Отладочная информация
    print(f"Debug: User {request.user.email}, is_profile_complete: {request.user.is_profile_complete()}")
    print(f"Debug: User fields - first_name: '{request.user.first_name}', last_name: '{request.user.last_name}', city: '{request.user.city}'")
    
    try:
        social_auths = request.user.social_auth.all()
        print(f"Debug: User has {len(social_auths)} social auth(s)")
        
        if social_auths:
            for social_auth in social_auths:
                print(f"Debug: Social auth provider: {social_auth.provider}")
                if social_auth.provider == 'google-oauth2':
                    provider_name = 'Google'
                elif social_auth.provider == 'github':
                    provider_name = 'GitHub'
                elif social_auth.provider == 'apple-id':
                    provider_name = 'Apple'
        else:
            print("Debug: No social auths found")
    except Exception as e:
        print(f"Debug: Error getting social auths: {e}")
    
    if request.method == 'POST':
        from .forms import ProfileCompletionForm
        form = ProfileCompletionForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.profile_completed = True
            user.save()
            
            # Отладочная информация после сохранения
            print(f"Debug: After save - profile_completed: {user.profile_completed}, is_profile_complete: {user.is_profile_complete()}")
            
            log_user_action(user, 'profile_completion', request)
            messages.success(request, 'Профиль успешно завершен! Добро пожаловать в EngAI!')
            return redirect('home')
    else:
        from .forms import ProfileCompletionForm
        # Предзаполняем форму данными пользователя
        form = ProfileCompletionForm(instance=request.user)
    
    return render(request, 'users/complete_profile.html', {
        'form': form,
        'provider_name': provider_name
    })

def register(request):
    if request.method == 'POST':
        # Получаем данные из формы
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        verification_code = request.POST.get('verification_code')

        # Проверяем, существует ли пользователь
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует')
            return render(request, 'users/registration.html')

        # Проверяем совпадение паролей
        if password1 != password2:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'users/registration.html')

        # Если это первый шаг (email и пароль)
        if email and password1 and not first_name:
            # Генерируем код подтверждения
            code = str(random.randint(100000, 999999))
            request.session['verification_code'] = code
            request.session['email'] = email
            request.session['password'] = password1

            # Отправляем код на email
            send_mail(
                'Код подтверждения',
                f'Ваш код подтверждения: {code}',
                'from@example.com',
                [email],
                fail_silently=False,
            )
            return render(request, 'users/registration.html')

        # Если это второй шаг (личные данные)
        elif first_name and last_name and phone_number:
            request.session['first_name'] = first_name
            request.session['last_name'] = last_name
            request.session['phone_number'] = phone_number
            return render(request, 'users/registration.html')

        # Если это третий шаг (подтверждение)
        elif verification_code:
            stored_code = request.session.get('verification_code')
            if verification_code == stored_code:
                # Создаем пользователя
                user = User.objects.create_user(
                    email=request.session.get('email'),
                    password=request.session.get('password'),
                    first_name=request.session.get('first_name'),
                    last_name=request.session.get('last_name'),
                    phone_number=request.session.get('phone_number')
                )
                
                # Очищаем сессию
                for key in ['verification_code', 'email', 'password', 'first_name', 'last_name', 'phone_number']:
                    request.session.pop(key, None)
                
                # Авторизуем пользователя с указанием бэкенда
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('home')
            else:
                messages.error(request, 'Неверный код подтверждения')
                return render(request, 'users/registration.html')

    return render(request, 'users/registration.html')

@require_POST
def resend_code(request):
    email = request.session.get('email')
    if email:
        # Генерируем новый код
        code = str(random.randint(100000, 999999))
        request.session['verification_code'] = code

        # Отправляем код на email
        send_mail(
            'Код подтверждения',
            f'Ваш код подтверждения: {code}',
            'from@example.com',
            [email],
            fail_silently=False,
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
def friends_view(request):
    """Основная страница друзей"""
    friends = Friendship.get_friends(request.user)
    pending_requests = Friendship.get_pending_requests(request.user)
    
    # Получаем данные о группах
    user_groups = StudyGroup.objects.filter(
        Q(creator=request.user) |
        Q(memberships__user=request.user, memberships__status='accepted')
    ).distinct()
    
    # Группы, созданные друзьями (доступные для присоединения)
    friends_groups = StudyGroup.objects.filter(
        creator__in=friends,
        is_active=True
    ).exclude(
        Q(creator=request.user) |
        Q(memberships__user=request.user)
    ).distinct()
    
    # Заявки в группы (для создателей групп)
    group_requests = StudyGroupMembership.objects.filter(
        group__creator=request.user,
        status='pending'
    )
    
    context = {
        'friends': friends,
        'pending_requests': pending_requests,
        'user_groups': user_groups,
        'friends_groups': friends_groups,
        'group_requests': group_requests,
        'active_tab': request.GET.get('tab', 'friends')  # friends, search, requests, groups
    }
    return render(request, 'users/friends.html', context)


@login_required
def search_friends(request):
    """Поиск пользователей для добавления в друзья"""
    query = request.GET.get('q', '').strip()
    results = []
    
    if query and len(query) >= 2:
        # Поиск по имени, фамилии и email
        users = User.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ).exclude(id=request.user.id)[:20]  # Ограничиваем 20 результатами
        
        for user in users:
            # Проверяем статус отношений
            is_friend = Friendship.are_friends(request.user, user)
            
            # Проверяем, есть ли отправленная заявка
            pending_request = Friendship.objects.filter(
                Q(from_user=request.user, to_user=user) | 
                Q(from_user=user, to_user=request.user),
                status='pending'
            ).first()
            
            status = 'none'
            if is_friend:
                status = 'friend'
            elif pending_request:
                if pending_request.from_user == request.user:
                    status = 'sent'
                else:
                    status = 'received'
            
            results.append({
                'id': user.id,
                'name': user.get_full_name() or user.email,
                'email': user.email,
                'level': user.get_current_language_level_display(),
                'level_code': user.current_language_level,
                'status': status
            })
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'results': results})
    
    return render(request, 'users/friends.html', {
        'search_results': results,
        'search_query': query,
        'active_tab': 'search',
        'friends': Friendship.get_friends(request.user),
        'pending_requests': Friendship.get_pending_requests(request.user),
    })


@login_required
@require_POST
def send_friend_request(request):
    """Отправка заявки в друзья"""
    import logging
    logger = logging.getLogger(__name__)
    
    user_id = request.POST.get('user_id')
    logger.info(f"Получен запрос на добавление в друзья от {request.user.id} к {user_id}")
    
    if not user_id:
        logger.error("Не указан user_id в запросе")
        return JsonResponse({
            'success': False,
            'message': 'Не указан ID пользователя'
        })
    
    try:
        to_user = User.objects.get(id=user_id)
        logger.info(f"Найден пользователь {to_user.email} для добавления в друзья")
        
        friendship, message = Friendship.send_friend_request(request.user, to_user)
        logger.info(f"Результат добавления в друзья: {friendship is not None}, сообщение: {message}")
        
        return JsonResponse({
            'success': friendship is not None,
            'message': message
        })
    except User.DoesNotExist:
        logger.error(f"Пользователь с ID {user_id} не найден")
        return JsonResponse({
            'success': False,
            'message': 'Пользователь не найден'
        })
    except Exception as e:
        logger.error(f"Неожиданная ошибка при добавлении в друзья: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при отправке заявки'
        })


@login_required
@require_POST 
def respond_friend_request(request):
    """Ответ на заявку в друзья"""
    request_id = request.POST.get('request_id')
    action = request.POST.get('action')  # 'accept' или 'decline'
    
    try:
        friendship = Friendship.objects.get(
            id=request_id,
            to_user=request.user,
            status='pending'
        )
        
        if action == 'accept':
            friendship.status = 'accepted'
            message = f'Вы теперь друзья с {friendship.from_user.get_full_name()}!'
        elif action == 'decline':
            friendship.status = 'declined'
            message = 'Заявка отклонена'
        else:
            return JsonResponse({
                'success': False,
                'message': 'Неверное действие'
            })
        
        friendship.save()
        
        return JsonResponse({
            'success': True,
            'message': message
        })
        
    except Friendship.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Заявка не найдена'
        })


@login_required
@require_POST
def remove_friend(request):
    """Удаление из друзей"""
    import logging
    logger = logging.getLogger(__name__)
    
    friend_id = request.POST.get('friend_id')
    logger.info(f"Получен запрос на удаление из друзей от {request.user.id} пользователя {friend_id}")
    
    if not friend_id:
        logger.error("Не указан friend_id в запросе")
        return JsonResponse({
            'success': False,
            'message': 'Не указан ID друга'
        })
    
    try:
        friend = User.objects.get(id=friend_id)
        logger.info(f"Найден пользователь {friend.email} для удаления из друзей")
        
        # Находим связь дружбы
        friendship = Friendship.objects.filter(
            Q(from_user=request.user, to_user=friend) |
            Q(from_user=friend, to_user=request.user),
            status='accepted'
        ).first()
        
        if friendship:
            logger.info(f"Найдена связь дружбы ID: {friendship.id}")
            friendship.delete()
            logger.info(f"Дружба успешно удалена")
            return JsonResponse({
                'success': True,
                'message': f'{friend.get_full_name() or friend.email} удален из друзей'
            })
        else:
            logger.warning(f"Дружба между {request.user.id} и {friend_id} не найдена")
            return JsonResponse({
                'success': False,
                'message': 'Дружба не найдена'
            })
            
    except User.DoesNotExist:
        logger.error(f"Пользователь с ID {friend_id} не найден")
        return JsonResponse({
            'success': False,
            'message': 'Пользователь не найден'
        })
    except Exception as e:
        logger.error(f"Неожиданная ошибка при удалении из друзей: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при удалении друга'
        })


@login_required
def messages_view(request):
    """Страница со списком чатов"""
    # Получаем все чаты пользователя
    user_chats = Chat.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).prefetch_related('messages').order_by('-updated_at')
    
    # Подготавливаем данные для шаблона
    chats_data = []
    for chat in user_chats:
        other_user = chat.get_other_user(request.user)
        last_message = chat.get_last_message()
        unread_count = chat.get_unread_count(request.user)
        
        chats_data.append({
            'chat': chat,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count,
        })
    
    # Поиск по чатам
    search_query = request.GET.get('q', '')
    if search_query:
        chats_data = [chat_data for chat_data in chats_data 
                     if search_query.lower() in (chat_data['other_user'].get_full_name() or chat_data['other_user'].email).lower()]
    
    return render(request, 'users/messages.html', {
        'chats_data': chats_data,
        'search_query': search_query,
    })


@login_required
def chat_view(request, user_id):
    """Страница чата с конкретным пользователем"""
    other_user = get_object_or_404(User, id=user_id)
    
    # Проверяем, что пользователи друзья (информационная безопасность)
    if not Friendship.are_friends(request.user, other_user):
        messages.error(request, 'Вы можете обмениваться сообщениями только с друзьями')
        return redirect('friends')
    
    # Получаем или создаем чат
    chat = Chat.get_or_create_chat(request.user, other_user)
    
    # Отмечаем сообщения как прочитанные
    chat.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    # Получаем сообщения с пагинацией
    messages_list = chat.messages.order_by('-created_at')
    paginator = Paginator(messages_list, 50)  # 50 сообщений на страницу
    
    page_number = request.GET.get('page')
    messages_page = paginator.get_page(page_number)
    
    # Обращаем порядок для отображения (сообщения сверху вниз)
    messages_page.object_list = list(reversed(messages_page.object_list))
    
    return render(request, 'users/chat.html', {
        'chat': chat,
        'other_user': other_user,
        'messages': messages_page,
    })


@login_required
@require_POST
def send_message(request):
    """Отправка сообщения"""
    chat_id = request.POST.get('chat_id')
    content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({
            'success': False,
            'message': 'Сообщение не может быть пустым'
        })
    
    try:
        chat = Chat.objects.get(id=chat_id)
        
        # Проверяем, что пользователь участвует в чате
        if request.user not in [chat.user1, chat.user2]:
            return JsonResponse({
                'success': False,
                'message': 'Нет доступа к этому чату'
            })
        
        # Создаем сообщение
        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            content=content,
            message_type='text'
        )
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
                'sender_name': message.sender.get_full_name() or message.sender.email,
                'sender_id': message.sender.id,
                'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
                'message_type': message.message_type,
            }
        })
        
    except Chat.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Чат не найден'
        })


@login_required
@require_POST
def upload_file(request):
    """Загрузка файла в чат"""
    from .file_validators import validate_chat_file, FileValidator
    from django.core.exceptions import ValidationError
    
    chat_id = request.POST.get('chat_id')
    uploaded_file = request.FILES.get('file')
    
    if not uploaded_file:
        return JsonResponse({
            'success': False,
            'message': 'Файл не выбран'
        })
    
    # Валидация файла с помощью безопасного валидатора
    try:
        validate_chat_file(uploaded_file)
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'message': ', '.join(e.messages)
        })
    
    # Очистка имени файла
    uploaded_file.name = FileValidator.sanitize_filename(uploaded_file.name)
    
    try:
        chat = Chat.objects.get(id=chat_id)
        
        # Проверяем, что пользователь участвует в чате
        if request.user not in [chat.user1, chat.user2]:
            return JsonResponse({
                'success': False,
                'message': 'Нет доступа к этому чату'
            })
        
        # Создаем сообщение с файлом
        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            file=uploaded_file,
            file_name=uploaded_file.name,
            file_size=uploaded_file.size
        )
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'sender_name': message.sender.get_full_name() or message.sender.email,
                'sender_id': message.sender.id,
                'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
                'message_type': message.message_type,
                'file_name': message.file_name,
                'file_size': message.file_size_human,
                'file_url': message.file.url if message.file else None,
                'is_image': message.is_image,
            }
        })
        
    except Chat.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Чат не найден'
        })


@login_required
def get_messages(request, chat_id):
    """Получение новых сообщений для AJAX"""
    try:
        chat = Chat.objects.get(id=chat_id)
        
        # Проверяем, что пользователь участвует в чате
        if request.user not in [chat.user1, chat.user2]:
            return JsonResponse({
                'success': False,
                'message': 'Нет доступа к этому чату'
            })
        
        # Получаем ID последнего сообщения
        last_message_id = request.GET.get('last_message_id', 0)
        
        # Получаем новые сообщения
        new_messages = chat.messages.filter(
            id__gt=last_message_id
        ).order_by('created_at')
        
        # Отмечаем как прочитанные
        new_messages.exclude(sender=request.user).update(is_read=True)
        
        messages_data = []
        for message in new_messages:
            message_data = {
                'id': message.id,
                'sender_name': message.sender.get_full_name() or message.sender.email,
                'sender_id': message.sender.id,
                'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
                'message_type': message.message_type,
            }
            
            if message.message_type == 'text':
                message_data['content'] = message.content
            else:
                message_data['file_name'] = message.file_name
                message_data['file_size'] = message.file_size_human
                message_data['file_url'] = message.file.url if message.file else None
                message_data['is_image'] = message.is_image
            
            messages_data.append(message_data)
        
        return JsonResponse({
            'success': True,
            'messages': messages_data
        })
        
    except Chat.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Чат не найден'
        })


# ==============================================
# ФУНКЦИИ ДЛЯ РАБОТЫ С УЧЕБНЫМИ ГРУППАМИ
# ==============================================

@login_required
@require_POST
def create_group(request):
    """Создание новой учебной группы"""
    import logging
    logger = logging.getLogger(__name__)
    
    name = request.POST.get('name', '').strip()
    
    logger.info(f"Получен запрос на создание группы от {request.user.id}: {name}")
    
    if not name:
        return JsonResponse({
            'success': False,
            'message': 'Название группы обязательно'
        })
    
    if len(name) > 100:
        return JsonResponse({
            'success': False,
            'message': 'Название группы слишком длинное'
        })
    
    try:
        # Проверяем, что у пользователя не слишком много групп
        user_groups_count = StudyGroup.objects.filter(creator=request.user, is_active=True).count()
        if user_groups_count >= 10:
            return JsonResponse({
                'success': False,
                'message': 'Вы можете создать не более 10 активных групп'
            })
        
        # Создаем группу
        group = StudyGroup.objects.create(
            name=name,
            description='',  # Пока без описания
            creator=request.user,
            max_members=30  # Фиксированное значение
        )
        
        # Создаем членство для создателя
        StudyGroupMembership.objects.create(
            group=group,
            user=request.user,
            status='accepted',
            role='creator'
        )
        
        # Создаем чат для группы
        GroupChat.objects.create(group=group)
        
        logger.info(f"Группа {name} успешно создана ID: {group.id}")
        
        return JsonResponse({
            'success': True,
            'message': f'Группа "{name}" создана успешно!',
            'group_id': group.id
        })
        
    except Exception as e:
        logger.error(f"Ошибка при создании группы: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при создании группы'
        })


@login_required
@require_POST
def join_group(request):
    """Отправка заявки на вступление в группу"""
    import logging
    logger = logging.getLogger(__name__)
    
    group_id = request.POST.get('group_id')
    
    if not group_id:
        return JsonResponse({
            'success': False,
            'message': 'Не указан ID группы'
        })
    
    try:
        group = StudyGroup.objects.get(id=group_id, is_active=True)
        
        # Проверяем, что создатель группы является другом
        if not Friendship.are_friends(request.user, group.creator):
            return JsonResponse({
                'success': False,
                'message': 'Вы можете присоединяться только к группам своих друзей'
            })
        
        # Проверяем, есть ли свободные места
        if not group.can_join():
            return JsonResponse({
                'success': False,
                'message': 'В группе нет свободных мест'
            })
        
        # Проверяем существующее членство
        existing_membership = StudyGroupMembership.objects.filter(
            group=group,
            user=request.user
        ).first()
        
        if existing_membership:
            if existing_membership.status == 'accepted':
                return JsonResponse({
                    'success': False,
                    'message': 'Вы уже являетесь участником этой группы'
                })
            elif existing_membership.status == 'pending':
                return JsonResponse({
                    'success': False,
                    'message': 'Ваша заявка уже отправлена'
                })
            else:
                existing_membership.status = 'pending'
                existing_membership.save()
                return JsonResponse({
                    'success': True,
                    'message': f'Заявка в группу "{group.name}" отправлена'
                })
        
        # Создаем новую заявку
        StudyGroupMembership.objects.create(
            group=group,
            user=request.user,
            status='pending'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Заявка в группу "{group.name}" отправлена'
        })
        
    except StudyGroup.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Группа не найдена'
        })
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка'
        })


@login_required
@require_POST
def edit_group(request):
    """Редактирование названия группы"""
    import logging
    logger = logging.getLogger(__name__)
    
    group_id = request.POST.get('group_id')
    new_name = request.POST.get('name', '').strip()
    
    if not group_id or not new_name:
        return JsonResponse({
            'success': False,
            'message': 'Необходимые параметры не указаны'
        })
    
    if len(new_name) > 100:
        return JsonResponse({
            'success': False,
            'message': 'Название группы слишком длинное'
        })
    
    try:
        group = StudyGroup.objects.get(
            id=group_id,
            creator=request.user,  # Только создатель может редактировать
            is_active=True
        )
        
        old_name = group.name
        group.name = new_name
        group.save()
        
        logger.info(f"Название группы изменено с '{old_name}' на '{new_name}'")
        
        # Добавляем системное сообщение в чат
        try:
            group_chat = GroupChat.objects.get(group=group)
            GroupMessage.objects.create(
                chat=group_chat,
                sender=request.user,
                message_type='system',
                content=f'Название группы изменено на "{new_name}"'
            )
        except GroupChat.DoesNotExist:
            pass
        
        return JsonResponse({
            'success': True,
            'message': f'Название группы изменено на "{new_name}"'
        })
        
    except StudyGroup.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Группа не найдена или у вас нет прав на редактирование'
        })
    except Exception as e:
        logger.error(f"Ошибка при редактировании группы: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при редактировании'
        })


@login_required
@require_POST
def delete_group(request):
    """Удаление группы"""
    import logging
    logger = logging.getLogger(__name__)
    
    group_id = request.POST.get('group_id')
    
    if not group_id:
        return JsonResponse({
            'success': False,
            'message': 'Не указан ID группы'
        })
    
    try:
        group = StudyGroup.objects.get(
            id=group_id,
            creator=request.user,  # Только создатель может удалять
            is_active=True
        )
        
        group_name = group.name
        
        # Мягкое удаление - просто отмечаем как неактивную
        group.is_active = False
        group.save()
        
        logger.info(f"Группа '{group_name}' удалена пользователем {request.user.id}")
        
        return JsonResponse({
            'success': True,
            'message': f'Группа "{group_name}" удалена'
        })
        
    except StudyGroup.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Группа не найдена или у вас нет прав на удаление'
        })
    except Exception as e:
        logger.error(f"Ошибка при удалении группы: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при удалении'
        })


@login_required
@require_POST
def respond_group_request(request):
    """Ответ на заявку в группу (принять/отклонить)"""
    import logging
    logger = logging.getLogger(__name__)
    
    request_id = request.POST.get('request_id')
    action = request.POST.get('action')  # 'accept' или 'decline'
    
    if not request_id or action not in ['accept', 'decline']:
        return JsonResponse({
            'success': False,
            'message': 'Неверные параметры запроса'
        })
    
    try:
        # Получаем заявку, где текущий пользователь является создателем группы
        membership = StudyGroupMembership.objects.get(
            id=request_id,
            group__creator=request.user,
            status='pending'
        )
        
        group = membership.group
        applicant = membership.user
        
        if action == 'accept':
            # Проверяем, есть ли место в группе
            if not group.can_join():
                return JsonResponse({
                    'success': False,
                    'message': 'В группе нет свободных мест'
                })
            
            membership.status = 'accepted'
            membership.role = 'member'
            membership.save()
            
            # Добавляем системное сообщение в групповой чат
            try:
                group_chat = GroupChat.objects.get(group=group)
                GroupMessage.objects.create(
                    chat=group_chat,
                    sender=request.user,
                    message_type='system',
                    content=f'{applicant.get_full_name() or applicant.email} присоединился к группе'
                )
            except GroupChat.DoesNotExist:
                pass
            
            message = f'{applicant.get_full_name() or applicant.email} принят в группу'
            
        elif action == 'decline':
            membership.status = 'declined'
            membership.save()
            
            message = f'Заявка от {applicant.get_full_name() or applicant.email} отклонена'
        
        logger.info(f"Заявка в группу '{group.name}' от {applicant.email} {action}ed")
        
        return JsonResponse({
            'success': True,
            'message': message
        })
        
    except StudyGroupMembership.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Заявка не найдена или у вас нет прав на её обработку'
        })
    except Exception as e:
        logger.error(f"Ошибка при обработке заявки в группу: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при обработке заявки'
        })


@login_required
@require_POST
def invite_to_group(request):
    """Приглашение друга в группу"""
    import logging
    logger = logging.getLogger(__name__)
    
    group_id = request.POST.get('group_id')
    friend_id = request.POST.get('friend_id')
    
    if not group_id or not friend_id:
        return JsonResponse({
            'success': False,
            'message': 'Необходимые параметры не указаны'
        })
    
    try:
        # Проверяем, что группа существует и пользователь является создателем или участником
        group = StudyGroup.objects.get(id=group_id, is_active=True)
        
        # Проверяем, что пользователь может приглашать (создатель или участник)
        if not (group.is_creator(request.user) or group.is_member(request.user)):
            return JsonResponse({
                'success': False,
                'message': 'У вас нет прав на приглашение в эту группу'
            })
        
        # Проверяем, что пользователь существует и является другом
        friend = User.objects.get(id=friend_id)
        
        if not Friendship.are_friends(request.user, friend):
            return JsonResponse({
                'success': False,
                'message': 'Можно приглашать только друзей'
            })
        
        # Проверяем, есть ли место в группе
        if not group.can_join():
            return JsonResponse({
                'success': False,
                'message': 'В группе нет свободных мест'
            })
        
        # Проверяем, нет ли уже членства или заявки
        existing_membership = StudyGroupMembership.objects.filter(
            group=group,
            user=friend
        ).first()
        
        if existing_membership:
            if existing_membership.status == 'accepted':
                return JsonResponse({
                    'success': False,
                    'message': f'{friend.get_full_name() or friend.email} уже в группе'
                })
            elif existing_membership.status == 'pending':
                return JsonResponse({
                    'success': False,
                    'message': f'Заявка от {friend.get_full_name() or friend.email} уже отправлена'
                })
            else:  # declined
                # Обновляем статус на pending (повторное приглашение)
                existing_membership.status = 'pending'
                existing_membership.save()
                return JsonResponse({
                    'success': True,
                    'message': f'{friend.get_full_name() or friend.email} приглашен в группу повторно'
                })
        
        # Создаем новое приглашение
        StudyGroupMembership.objects.create(
            group=group,
            user=friend,
            status='pending'
        )
        
        logger.info(f"Приглашение в группу '{group.name}' отправлено пользователю {friend.email}")
        
        return JsonResponse({
            'success': True,
            'message': f'{friend.get_full_name() or friend.email} приглашен в группу'
        })
        
    except StudyGroup.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Группа не найдена'
        })
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Пользователь не найден'
        })
    except Exception as e:
        logger.error(f"Ошибка при приглашении: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при отправке приглашения'
        })


