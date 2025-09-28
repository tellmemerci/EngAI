# users/urls.py
from django.urls import path
from .views import (
    registration_view, 
    login_view, 
    logout_view, 
    change_password_view, 
    index_view, 
    profile_view,
    sms_verification_view
)
from django.views.generic import TemplateView

urlpatterns = [
    path('', login_view, name='index'),
    path('register/', registration_view, name='register'),
    path('sms-verification/', sms_verification_view, name='sms_verification'),
    path('login/', login_view, name='login'),
    path('accounts/login/', login_view, name='accounts_login'),
    path('logout/', logout_view, name='logout'),
    path('password-reset/', change_password_view, name='password_reset'),
    path('home/', index_view, name='home'),
    path('profile/', profile_view, name='profile'),
    path('test/', TemplateView.as_view(template_name='users/test.html'), name='test'),
]