from django import forms
from .models import StudyModule, ModuleSection, ModuleSkill, TheoryCard, ModuleAttachment, Unit, Topic, UnitSection, UnitSkill, UnitTheoryCard, UnitAttachment, GrammarTask, ModuleAccessRequest, UserModuleAccess

class StudyModuleForm(forms.ModelForm):
    class Meta:
        model = StudyModule
        fields = ['title', 'description', 'image', 'module_type', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название модуля'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите описание модуля',
                'rows': 5
            }),
            'module_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'image': 'Изображение',
            'module_type': 'Тип модуля',
            'is_published': 'Опубликовать'
        }
        help_texts = {
            'image': 'Рекомендуемый размер: 1200x800 пикселей',
            'is_published': 'Отметьте, если хотите сразу опубликовать модуль'
        }


class ModuleSectionForm(forms.ModelForm):
    class Meta:
        model = ModuleSection
        fields = ['title', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название секции'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание секции',
                'rows': 3
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            })
        }


class TheoryCardForm(forms.ModelForm):
    class Meta:
        model = TheoryCard
        fields = ['title', 'content', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название карточки'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Содержание карточки',
                'rows': 4
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            })
        }


class ModuleSkillForm(forms.ModelForm):
    class Meta:
        model = ModuleSkill
        fields = ['skill_type', 'title', 'description', 'is_available', 'order']
        widgets = {
            'skill_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название навыка'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание навыка',
                'rows': 3
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            })
        }


class ModuleAttachmentForm(forms.ModelForm):
    class Meta:
        model = ModuleAttachment
        fields = ['file_type', 'title', 'file', 'description', 'file_size', 'order']
        widgets = {
            'file_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название файла'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Описание файла'
            }),
            'file_size': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Размер файла'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            })
        } 


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['title', 'description', 'image', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название юнита'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание юнита',
                'rows': 5
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            })
        }
        labels = {
            'title': 'Название юнита',
            'description': 'Описание юнита',
            'image': 'Изображение юнита',
            'order': 'Порядок'
        }


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title', 'theory_content', 'practice_content', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название темы'
            }),
            'theory_content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Теоретическая часть',
                'rows': 5
            }),
            'practice_content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Практическая часть',
                'rows': 5
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            })
        }
        labels = {
            'title': 'Название темы',
            'theory_content': 'Теоретическая часть',
            'practice_content': 'Практическая часть',
            'order': 'Порядок'
        }


class UnitSectionForm(forms.ModelForm):
    class Meta:
        model = UnitSection
        fields = ['title', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название секции'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание секции',
                'rows': 3
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            })
        }


class UnitSkillForm(forms.ModelForm):
    class Meta:
        model = UnitSkill
        fields = ['skill_type', 'title', 'description', 'is_available', 'order']
        widgets = {
            'skill_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название навыка'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание навыка',
                'rows': 3
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            })
        }


class UnitTheoryCardForm(forms.ModelForm):
    class Meta:
        model = UnitTheoryCard
        fields = ['title', 'content', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название карточки'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Содержание карточки',
                'rows': 4
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            })
        }


class UnitAttachmentForm(forms.ModelForm):
    class Meta:
        model = UnitAttachment
        fields = ['file_type', 'title', 'file', 'description', 'file_size', 'order']
        widgets = {
            'file_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название файла'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Описание файла'
            }),
            'file_size': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Размер файла'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            })
        } 


class ModuleAccessRequestForm(forms.ModelForm):
    """Форма для подачи заявки на доступ к закрытому модулю"""
    class Meta:
        model = ModuleAccessRequest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Опишите, зачем вам нужен доступ к этому модулю...',
                'rows': 4
            })
        }
        labels = {
            'message': 'Сообщение для автора'
        }
        help_texts = {
            'message': 'Расскажите автору модуля, почему вам нужен доступ'
        }


class ModulePasswordForm(forms.Form):
    """Форма для ввода пароля к закрытому модулю"""
    password = forms.CharField(
        label='Пароль доступа',
        max_length=255,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль для доступа к модулю'
        }),
        help_text='Введите пароль, который предоставил автор модуля'
    )


class SetModulePasswordForm(forms.Form):
    """Форма для установки пароля к модулю (для автора)"""
    password = forms.CharField(
        label='Новый пароль',
        max_length=255,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль для доступа к модулю'
        }),
        help_text='Этот пароль смогут использовать пользователи для получения доступа'
    )
    confirm_password = forms.CharField(
        label='Подтвердите пароль',
        max_length=255,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Пароли не совпадают.')
        
        return cleaned_data


class ReviewAccessRequestForm(forms.ModelForm):
    """Форма для рассмотрения заявки на доступ (для автора)"""
    class Meta:
        model = ModuleAccessRequest
        fields = ['status', 'reviewer_message']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'reviewer_message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Комментарий для пользователя (необязательно)',
                'rows': 3
            })
        }
        labels = {
            'status': 'Решение по заявке',
            'reviewer_message': 'Комментарий'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ограничиваем выбор статусов только approved и rejected
        self.fields['status'].choices = [
            ('approved', 'Одобрить'),
            ('rejected', 'Отклонить'),
        ]
