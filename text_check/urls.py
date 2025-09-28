from django.urls import path
from . import views

app_name = 'text_check'

urlpatterns = [
    path('', views.text_check_view, name='text_check'),
    path('check/', views.check_text, name='check_text'),
    path('history/', views.text_check_history, name='text_check_history'),
] 