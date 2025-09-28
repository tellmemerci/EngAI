from django.urls import path
from . import views

app_name = 'modules'

urlpatterns = [
    path('<int:module_id>/unit/<int:unit_id>/topic/<int:topic_id>/add-task/', views.add_task, name='add_task'),
    path('<int:module_id>/unit/<int:unit_id>/topic/<int:topic_id>/task/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('<int:module_id>/unit/<int:unit_id>/topic/<int:topic_id>/task/<int:task_id>/delete/', views.delete_task, name='delete_task'),
]
