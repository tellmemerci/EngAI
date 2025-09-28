from django.urls import path
from . import views

urlpatterns = [
    path('', views.dictionary_view, name='dictionary'),
    path('api/saved-words/', views.saved_words, name='saved_words'),
    path('api/frequent-words/', views.frequent_words, name='frequent_words'),
    path('api/save-word/', views.save_word, name='save_word'),
    path('api/delete-word/', views.delete_word, name='delete_word'),
    path('api/text-to-speech/', views.text_to_speech, name='text_to_speech'),
] 