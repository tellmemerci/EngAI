from django import forms
from .models import GrammarTask


class GrammarTaskForm(forms.ModelForm):
    class Meta:
        model = GrammarTask
        fields = ['task_type', 'title', 'description', 'instruction', 'content', 'correct_answer', 'order', 'is_active']
        widgets = {
            'task_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название задания'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание задания',
                'rows': 3
            }),
            'instruction': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Инструкция для выполнения',
                'rows': 2
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'JSON содержимое задания',
                'rows': 8
            }),
            'correct_answer': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'JSON правильный ответ',
                'rows': 4
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
