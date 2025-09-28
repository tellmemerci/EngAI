from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, PasswordChangeForm
from .utils import log_user_action, generate_sms_code, send_sms_code
from django.core.exceptions import ValidationError
from .models import User
from django.core.mail import send_mail
import random
from django.http import JsonResponse
from django.views.decorators.http import require_POST

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
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.city = request.POST.get('city', user.city)
        user.birth_date = request.POST.get('birth_date', user.birth_date)
        user.current_language_level = request.POST.get('current_language_level', user.current_language_level)
        user.desired_language_level = request.POST.get('desired_language_level', user.desired_language_level)
        user.save()
        messages.success(request, 'Профиль успешно обновлен')
        return redirect('profile')
    
    return render(request, 'users/profile.html')

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