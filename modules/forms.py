from django import forms
from .models import Task, TaskOption

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['topic', 'task_block', 'task_type', 'prompt', 'description', 'media_image', 'media_audio', 'correct_answer']
        widgets = {
            'topic': forms.Select(attrs={'class': 'form-control'}),
            'task_block': forms.Select(attrs={'class': 'form-control'}),
            'task_type': forms.Select(attrs={'class': 'form-control'}),
            'prompt': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'media_image': forms.FileInput(attrs={'class': 'form-control'}),
            'media_audio': forms.FileInput(attrs={'class': 'form-control'}),
            'correct_answer': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'topic': 'Тема',
            'task_block': 'Блок заданий',
            'task_type': 'Тип задания',
            'prompt': 'Неправильное или условное предложение',
            'description': 'Описание задания / инструкция',
            'media_image': 'Изображение к заданию',
            'media_audio': 'Аудио к заданию',
            'correct_answer': 'Правильный ответ',
        }

class TaskOptionForm(forms.ModelForm):
    class Meta:
        model = TaskOption
        fields = ['task', 'text', 'is_correct', 'image', 'audio']
        widgets = {
            'task': forms.Select(attrs={'class': 'form-control'}),
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'audio': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'task': 'Задание',
            'text': 'Вариант ответа',
            'is_correct': 'Это правильный вариант?',
            'image': 'Изображение варианта',
            'audio': 'Аудио варианта',
        }
