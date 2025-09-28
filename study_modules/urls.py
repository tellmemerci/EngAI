from django.urls import path
from . import views

app_name = 'study_modules'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('<int:module_id>/', views.detail, name='detail'),
    path('<int:module_id>/structure/', views.module_structure, name='module_structure'),
    path('<int:module_id>/detail/', views.module_detail, name='module_detail'),
    path('<int:module_id>/unit/<int:unit_id>/', views.unit_detail, name='unit_detail'),
    path('<int:module_id>/unit/<int:unit_id>/topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    path('<int:module_id>/section/<int:section_id>/card/<int:card_id>/', views.theory_card_detail, name='theory_card_detail'),
    path('<int:module_id>/edit/', views.edit_module_content, name='edit_module'),
    path('<int:module_id>/save/', views.save_module, name='save_module'),
    path('<int:module_id>/add-section/', views.add_section, name='add_section'),
    path('<int:module_id>/add-skill/', views.add_skill, name='add_skill'),
    path('<int:module_id>/add-attachment/', views.add_attachment, name='add_attachment'),
    path('<int:module_id>/section/<int:section_id>/add-card/', views.add_theory_card, name='add_theory_card'),
    path('<int:module_id>/add-unit/', views.add_unit, name='add_unit'),
    path('<int:module_id>/unit/<int:unit_id>/edit/', views.edit_unit, name='edit_unit'),
    path('<int:module_id>/unit/<int:unit_id>/delete/', views.delete_unit, name='delete_unit'),
    path('<int:module_id>/unit/<int:unit_id>/add-topic/', views.add_topic, name='add_topic'),
    path('<int:module_id>/unit/<int:unit_id>/topic/<int:topic_id>/edit/', views.edit_topic, name='edit_topic'),
    path('<int:module_id>/unit/<int:unit_id>/topic/<int:topic_id>/delete/', views.delete_topic, name='delete_topic'),
    path('<int:module_id>/unit/<int:unit_id>/edit-content/', views.edit_unit_content, name='edit_unit_content'),
    path('<int:module_id>/unit/<int:unit_id>/add-section/', views.add_unit_section, name='add_unit_section'),
    path('<int:module_id>/unit/<int:unit_id>/add-skill/', views.add_unit_skill, name='add_unit_skill'),
    path('<int:module_id>/unit/<int:unit_id>/add-attachment/', views.add_unit_attachment, name='add_unit_attachment'),
    path('<int:module_id>/unit/<int:unit_id>/section/<int:section_id>/add-card/', views.add_unit_theory_card, name='add_unit_theory_card'),
    path('<int:module_id>/unit/<int:unit_id>/section/<int:section_id>/card/<int:card_id>/', views.unit_theory_card_detail, name='unit_theory_card_detail'),
    path('<int:module_id>/unit/<int:unit_id>/card/<int:card_id>/edit/', views.edit_unit_theory_card, name='edit_unit_theory_card'),
    path('<int:module_id>/unit/<int:unit_id>/card/<int:card_id>/delete/', views.delete_unit_theory_card, name='delete_unit_theory_card'),
    path('<int:module_id>/unit/<int:unit_id>/skill/<int:skill_id>/grammar-practice/', views.grammar_practice, name='grammar_practice'),
    path('<int:module_id>/unit/<int:unit_id>/skill/<int:skill_id>/add-task/', views.add_grammar_task, name='add_grammar_task'),
    path('<int:module_id>/unit/<int:unit_id>/skill/<int:skill_id>/task/<int:task_id>/edit/', views.edit_grammar_task, name='edit_grammar_task'),
    path('<int:module_id>/unit/<int:unit_id>/skill/<int:skill_id>/task/<int:task_id>/delete/', views.delete_grammar_task, name='delete_grammar_task'),
] 