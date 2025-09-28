from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from .models import StudyModule, ModuleSection, ModuleSkill, TheoryCard, ModuleAttachment, Unit, Topic, UnitSection, UnitSkill, UnitTheoryCard, UnitAttachment, GrammarTask
from .forms import StudyModuleForm, ModuleSectionForm, TheoryCardForm, ModuleSkillForm, ModuleAttachmentForm, UnitForm, TopicForm, UnitSectionForm, UnitSkillForm, UnitTheoryCardForm, UnitAttachmentForm
from .grammar_forms import GrammarTaskForm

# Create your views here.

@login_required
def index(request):
    tab = request.GET.get('tab', 'all')
    
    if tab == 'saved':
        # Только модули, сохраненные текущим пользователем
        modules = StudyModule.objects.filter(saved_by=request.user)
    elif tab == 'my':
        # Все опубликованные модули
        modules = StudyModule.objects.filter(is_published=True)
    else:  # all
        # Только модули, созданные текущим пользователем
        modules = StudyModule.objects.filter(author=request.user)
    
    context = {
        'modules': modules,
        'active_tab': tab
    }
    return render(request, 'study_modules/index.html', context)

@login_required
def detail(request, module_id):
    module = get_object_or_404(StudyModule, pk=module_id)
    context = {
        'module': module
    }
    return render(request, 'study_modules/detail.html', context)

@login_required
def create(request):
    if request.method == 'POST':
        form = StudyModuleForm(request.POST, request.FILES)
        if form.is_valid():
            module = form.save(commit=False)
            module.author = request.user
            module.is_published = True  # Автоматически публикуем модуль при создании
            module.save()
            messages.success(request, 'Модуль успешно создан!')
            return redirect('study_modules:detail', module_id=module.id)
    else:
        form = StudyModuleForm()
    
    context = {
        'form': form,
        'title': 'Создание модуля'
    }
    return render(request, 'study_modules/module_form.html', context)

@login_required
def module_structure(request, module_id):
    module = get_object_or_404(StudyModule, pk=module_id)
    context = {
        'module': module,
    }
    return render(request, 'study_modules/structure.html', context)

@login_required
@csrf_protect
def save_module(request, module_id):
    if request.method == 'POST':
        try:
            module = get_object_or_404(StudyModule, pk=module_id)
            is_saved = request.user in module.saved_by.all()
            
            if is_saved:
                module.saved_by.remove(request.user)
                return JsonResponse({
                    'status': 'success',
                    'action': 'removed',
                    'button_text': 'Сохранить модуль',
                    'button_icon': 'bookmark'
                })
            else:
                module.saved_by.add(request.user)
                return JsonResponse({
                    'status': 'success',
                    'action': 'saved',
                    'button_text': 'Удалить из сохраненных',
                    'button_icon': 'bookmark-check'
                })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    return JsonResponse({'status': 'error', 'message': 'Метод не поддерживается'}, status=405)


@login_required
def module_detail(request, module_id):
    """Детальная страница модуля с полной структурой"""
    module = get_object_or_404(StudyModule, pk=module_id)
    
    # Получаем юниты модуля и предварительно загружаем темы для каждого юнита
    units = Unit.objects.filter(module=module).order_by('order', 'title', 'id').prefetch_related('topics')

    # Получаем секции модуля
    theory_sections = ModuleSection.objects.filter(module=module, section_type='theory').order_by('order')
    practice_sections = ModuleSection.objects.filter(module=module, section_type='practice').order_by('order')
    
    # Получаем навыки модуля
    skills = ModuleSkill.objects.filter(module=module).order_by('order')
    
    # Получаем прикрепленные файлы
    attachments = ModuleAttachment.objects.filter(module=module).order_by('order')
    
    context = {
        'module': module,
        'theory_sections': theory_sections,
        'practice_sections': practice_sections,
        'skills': skills,
        'attachments': attachments,
        'units': units, # Добавляем юниты в контекст
    }
    return render(request, 'study_modules/module_detail.html', context)


@login_required
def edit_module_content(request, module_id):
    """Редактирование содержимого модуля"""
    module = get_object_or_404(StudyModule, pk=module_id)
    
    # Проверяем права доступа
    if module.author != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого модуля.')
        return redirect('study_modules:module_detail', module_id=module_id)
    
    if request.method == 'POST':
        # Обработка формы редактирования
        # Здесь будет логика сохранения изменений
        messages.success(request, 'Содержимое модуля успешно обновлено!')
        return redirect('study_modules:module_detail', module_id=module_id)
    
    # Получаем все данные модуля для редактирования
    theory_sections = ModuleSection.objects.filter(module=module, section_type='theory').order_by('order')
    practice_sections = ModuleSection.objects.filter(module=module, section_type='practice').order_by('order')
    skills = ModuleSkill.objects.filter(module=module).order_by('order')
    attachments = ModuleAttachment.objects.filter(module=module).order_by('order')
    
    context = {
        'module': module,
        'theory_sections': theory_sections,
        'practice_sections': practice_sections,
        'skills': skills,
        'attachments': attachments,
    }
    return render(request, 'study_modules/edit_module.html', context)


@login_required
def add_section(request, module_id):
    """Добавление новой секции к модулю"""
    module = get_object_or_404(StudyModule, pk=module_id)
    
    if module.author != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого модуля.')
        return redirect('study_modules:module_detail', module_id=module_id)
    
    if request.method == 'POST':
        form = ModuleSectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.module = module
            section.section_type = request.GET.get('section_type', 'theory')
            section.save()
            messages.success(request, 'Секция успешно добавлена!')
            return redirect('study_modules:edit_module', module_id=module_id)
    else:
        form = ModuleSectionForm()
    
    context = {
        'module': module,
        'form': form,
        'form_type': 'section'
    }
    return render(request, 'study_modules/add_item.html', context)


@login_required
def add_theory_card(request, module_id, section_id):
    """Добавление теоретической карточки"""
    module = get_object_or_404(StudyModule, pk=module_id)
    section = get_object_or_404(ModuleSection, pk=section_id, module=module)
    
    if module.author != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого модуля.')
        return redirect('study_modules:module_detail', module_id=module_id)
    
    if request.method == 'POST':
        form = TheoryCardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.section = section
            card.save()
            messages.success(request, 'Карточка успешно добавлена!')
            return redirect('study_modules:edit_module', module_id=module_id)
    else:
        form = TheoryCardForm()
    
    context = {
        'module': module,
        'section': section,
        'form': form,
        'form_type': 'theory_card'
    }
    return render(request, 'study_modules/add_item.html', context)


@login_required
def add_skill(request, module_id):
    """Добавление нового навыка к модулю"""
    module = get_object_or_404(StudyModule, pk=module_id)
    
    if module.author != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого модуля.')
        return redirect('study_modules:module_detail', module_id=module_id)
    
    if request.method == 'POST':
        form = ModuleSkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.module = module
            skill.save()
            messages.success(request, 'Навык успешно добавлен!')
            return redirect('study_modules:edit_module', module_id=module_id)
    else:
        form = ModuleSkillForm()
    
    context = {
        'module': module,
        'form': form,
        'form_type': 'skill'
    }
    return render(request, 'study_modules/add_item.html', context)


@login_required
def add_attachment(request, module_id):
    """Добавление прикрепленного файла к модулю"""
    module = get_object_or_404(StudyModule, pk=module_id)
    
    if module.author != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого модуля.')
        return redirect('study_modules:module_detail', module_id=module_id)
    
    if request.method == 'POST':
        form = ModuleAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.module = module
            attachment.save()
            messages.success(request, 'Файл успешно добавлен!')
            return redirect('study_modules:edit_module', module_id=module_id)
    else:
        form = ModuleAttachmentForm()
    
    context = {
        'module': module,
        'form': form,
        'form_type': 'attachment'
    }
    return render(request, 'study_modules/add_item.html', context)


@login_required
def add_unit(request, module_id):
    module = get_object_or_404(StudyModule, pk=module_id)

    if module.author != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого модуля.')
        return redirect('study_modules:module_detail', module_id=module_id)

    if request.method == 'POST':
        form = UnitForm(request.POST, request.FILES)
        if form.is_valid():
            unit = form.save(commit=False)
            unit.module = module
            unit.save()
            messages.success(request, 'Юнит успешно добавлен!')
            return redirect('study_modules:module_detail', module_id=module_id)
    else:
        form = UnitForm()

    context = {
        'module': module,
        'form': form,
        'form_type': 'unit',
        'title': 'Добавление юнита'
    }
    return render(request, 'study_modules/add_item.html', context)


@login_required
def edit_unit(request, module_id, unit_id):
    module = get_object_or_404(StudyModule, pk=module_id)
    unit = get_object_or_404(Unit, pk=unit_id, module=module)

    if module.author != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого модуля.')
        return redirect('study_modules:module_detail', module_id=module_id)

    if request.method == 'POST':
        form = UnitForm(request.POST, request.FILES, instance=unit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Юнит успешно обновлен!')
            return redirect('study_modules:module_detail', module_id=module_id)
    else:
        form = UnitForm(instance=unit)

    context = {
        'module': module,
        'unit': unit,
        'form': form,
        'form_type': 'unit',
        'title': 'Редактирование юнита'
    }
    return render(request, 'study_modules/add_item.html', context)


@login_required
def delete_unit(request, module_id, unit_id):
    module = get_object_or_404(StudyModule, pk=module_id)
    unit = get_object_or_404(Unit, pk=unit_id, module=module)

    if module.author != request.user:
        messages.error(request, 'У вас нет прав для удаления этого юнита.')
        return redirect('study_modules:module_detail', module_id=module_id)

    if request.method == 'POST':
        unit.delete()
        messages.success(request, 'Юнит успешно удален!')
        return redirect('study_modules:module_detail', module_id=module_id)

    context = {
        'module': module,
        'unit': unit,
        'title': 'Удаление юнита'
    }
    return render(request, 'study_modules/confirm_delete.html', context)


@login_required
def unit_detail(request, module_id, unit_id):
    module = get_object_or_404(StudyModule, pk=module_id)
    unit = get_object_or_404(Unit, pk=unit_id, module=module)

    # Получаем секции юнита (не модуля!)
    theory_sections = UnitSection.objects.filter(unit=unit, section_type='theory').order_by('order')
    practice_sections = UnitSection.objects.filter(unit=unit, section_type='practice').order_by('order')
    
    # Получаем навыки юнита (не модуля!)
    skills = UnitSkill.objects.filter(unit=unit).order_by('order')
    
    # Получаем прикрепленные файлы юнита (не модуля!)
    attachments = UnitAttachment.objects.filter(unit=unit).order_by('order')
    
    # Получаем темы юнита
    topics = Topic.objects.filter(unit=unit).order_by('order')
    
    # Получаем прикрепленные модули карточек к этому учебному модулю
    from .models import ModuleCardModule
    attached_card_modules = ModuleCardModule.objects.filter(study_module=module).select_related('card_module')

    context = {
        'module': module,
        'unit': unit,
        'theory_sections': theory_sections,
        'practice_sections': practice_sections,
        'skills': skills,
        'attachments': attachments,
        'topics': topics,
        'attached_card_modules': attached_card_modules,
    }
    return render(request, 'study_modules/unit_detail.html', context)


@login_required
def topic_detail(request, module_id, unit_id, topic_id):
    module = get_object_or_404(StudyModule, pk=module_id)
    unit = get_object_or_404(Unit, pk=unit_id, module=module)
    topic = get_object_or_404(Topic, pk=topic_id, unit=unit)

    if request.method == 'POST':
        # Only author can edit
        if module.author != request.user:
            messages.error(request, 'У вас нет прав для редактирования этого модуля.')
            return redirect('study_modules:topic_detail', module_id=module_id, unit_id=unit_id, topic_id=topic_id)

        content = request.POST.get('content', '')
        topic.theory_content = content
        topic.save()
        messages.success(request, 'Теоретический материал сохранен!')
        return redirect('study_modules:topic_detail', module_id=module_id, unit_id=unit_id, topic_id=topic_id)

    context = {
        'module': module,
        'unit': unit,
        'topic': topic,
    }
    return render(request, 'study_modules/topic_detail.html', context)


@login_required
def theory_card_detail(request, module_id, section_id, card_id):
    """Страница теоретической карточки с тем же редактором"""
    module = get_object_or_404(StudyModule, pk=module_id)
    section = get_object_or_404(ModuleSection, pk=section_id, module=module)
    card = get_object_or_404(TheoryCard, pk=card_id, section=section)

    if request.method == 'POST':
        if module.author != request.user:
            messages.error(request, 'У вас нет прав для редактирования этого модуля.')
            return redirect('study_modules:theory_card_detail', module_id=module_id, section_id=section_id, card_id=card_id)
        content = request.POST.get('content', '')
        card.content = content
        card.save()
        messages.success(request, 'Теоретическая карточка сохранена!')
        return redirect('study_modules:theory_card_detail', module_id=module_id, section_id=section_id, card_id=card_id)

    # Переиспользуем шаблон топика, но прокинем нужные поля
    context = {
        'module': module,
        'unit': None,
        'topic': type('Obj', (), {'title': card.title, 'theory_content': card.content})(),
        'back_url': 'study_modules:module_detail',
    }
    return render(request, 'study_modules/topic_detail.html', context)

@login_required
def add_topic(request, module_id, unit_id):
    module = get_object_or_404(StudyModule, pk=module_id)
    unit = get_object_or_404(Unit, pk=unit_id, module=module)

    if module.author != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого модуля.')
        return redirect('study_modules:module_detail', module_id=module_id)

    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.unit = unit
            topic.save()
            messages.success(request, 'Тема успешно добавлена!')
            return redirect('study_modules:unit_detail', module_id=module_id, unit_id=unit_id)
    else:
        form = TopicForm()

    context = {
        'module': module,
        'unit': unit,
        'form': form,
        'form_type': 'topic',
        'title': 'Добавление темы'
    }
    return render(request, 'study_modules/add_item.html', context)


@login_required
def edit_topic(request, module_id, unit_id, topic_id):
    module = get_object_or_404(StudyModule, pk=module_id)
    unit = get_object_or_404(Unit, pk=unit_id, module=module)
    topic = get_object_or_404(Topic, pk=topic_id, unit=unit)

    if module.author != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого модуля.')
        return redirect('study_modules:module_detail', module_id=module_id)

    if request.method == 'POST':
        form = TopicForm(request.POST, instance=topic)
        if form.is_valid():
            form.save()
            messages.success(request, 'Тема успешно обновлена!')
            return redirect('study_modules:unit_detail', module_id=module_id, unit_id=unit_id)
    else:
        form = TopicForm(instance=topic)

    context = {
        'module': module,
        'unit': unit,
        'topic': topic,
        'form': form,
        'form_type': 'topic',
        'title': 'Редактирование темы'
    }
    return render(request, 'study_modules/add_item.html', context)


@login_required
def delete_topic(request, module_id, unit_id, topic_id):
    module = get_object_or_404(StudyModule, pk=module_id)
    unit = get_object_or_404(Unit, pk=unit_id, module=module)
    topic = get_object_or_404(Topic, pk=topic_id, unit=unit)

    if module.author != request.user:
        messages.error(request, 'У вас нет прав для удаления этой темы.')
        return redirect('study_modules:module_detail', module_id=module_id)

    if request.method == 'POST':
        topic.delete()
        messages.success(request, 'Тема успешно удалена!')
        return redirect('study_modules:unit_detail', module_id=module_id, unit_id=unit_id)

    context = {
        'module': module,
        'unit': unit,
        'topic': topic,
        'title': 'Удаление темы'
    }
    return render(request, 'study_modules/confirm_delete.html', context)


@login_required
def edit_unit_content(request, module_id, unit_id):
    """Редактирование контента юнита (теория и практика)"""
    module = get_object_or_404(StudyModule, pk=module_id)
    unit = get_object_or_404(Unit, pk=unit_id, module=module)
    
    if module.author != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого юнита.')
        return redirect('study_modules:unit_detail', module_id=module_id, unit_id=unit_id)
    
    # Получаем все темы юнита
    topics = unit.topics.all().order_by('order')
    
    if request.method == 'POST':
        # Обработка сохранения изменений
        for topic in topics:
            topic_id = str(topic.id)
            theory_content = request.POST.get(f'theory_{topic_id}', '')
            practice_content = request.POST.get(f'practice_{topic_id}', '')
            
            topic.theory_content = theory_content
            topic.practice_content = practice_content
            topic.save()
        
        messages.success(request, 'Контент юнита успешно обновлен!')
        return redirect('study_modules:unit_detail', module_id=module_id, unit_id=unit_id)
    
    context = {
        'module': module,
        'unit': unit,
        'topics': topics,
    }
    return render(request, 'study_modules/edit_unit_content.html', context)


@login_required
def add_unit_section(request, module_id, unit_id):
    """Добавление новой секции к юниту"""
    module = get_object_or_404(StudyModule, pk=module_id)
    unit = get_object_or_404(Unit, pk=unit_id, module=module)
    
    if module.author != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого юнита.')
        return redirect('study_modules:unit_detail', module_id=module_id, unit_id=unit_id)
    
    if request.method == 'POST':
        form = UnitSectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.unit = unit
            section.section_type = request.GET.get('section_type', 'theory')
            section.save()
            messages.success(request, 'Секция успешно добавлена!')
            return redirect('study_modules:unit_detail', module_id=module_id, unit_id=unit_id)
    else:
        form = UnitSectionForm()
    
    context = {
        'module': module,
        'unit': unit,
        'form': form,
        'form_type': 'unit_section'
    }
    return render(request, 'study_modules/add_item.html', context)


@login_required
def add_unit_skill(request, module_id, unit_id):
    """Добавление нового навыка к юниту"""
    module = get_object_or_404(StudyModule, pk=module_id)
    unit = get_object_or_404(Unit, pk=unit_id, module=module)
    
    if module.author != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого юнита.')
        return redirect('study_modules:unit_detail', module_id=module_id, unit_id=unit_id)
    
    if request.method == 'POST':
        form = UnitSkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.unit = unit
            skill.save()
            messages.success(request, 'Навык успешно добавлен!')
            return redirect('study_modules:unit_detail', module_id=module_id, unit_id=unit_id)
    else:
        form = UnitSkillForm()
    
    context = {
        'module': module,
        'unit': unit,
        'form': form,
        'form_type': 'unit_skill'
    }
    return render(request, 'study_modules/add_item.html', context)


@login_required
def add_unit_attachment(request, module_id, unit_id):
    """Добавление прикрепленного файла к юниту"""
    module = get_object_or_404(StudyModule, pk=module_id)
    unit = get_object_or_404(Unit, pk=unit_id, module=module)
    
    if module.author != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого юнита.')
        return redirect('study_modules:unit_detail', module_id=module_id, unit_id=unit_id)
    
    if request.method == 'POST':
        form = UnitAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.unit = unit
            attachment.save()
            messages.success(request, 'Файл успешно добавлен!')
            return redirect('study_modules:unit_detail', module_id=module_id, unit_id=unit_id)
    else:
        form = UnitAttachmentForm()
    
    context = {
        'module': module,
        'unit': unit,
        'form': form,
        'form_type': 'unit_attachment'
    }
    return render(request, 'study_modules/add_item.html', context)


@login_required
def add_unit_theory_card(request, module_id, unit_id, section_id):
    """Добавление теоретической карточки к секции юнита"""
    module = get_object_or_404(StudyModule, pk=module_id)
    unit = get_object_or_404(Unit, pk=unit_id, module=module)
    section = get_object_or_404(UnitSection, pk=section_id, unit=unit)
    
    if module.author != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого юнита.')
        return redirect('study_modules:unit_detail', module_id=module_id, unit_id=unit_id)
    
    if request.method == 'POST':
        form = UnitTheoryCardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.section = section
            card.save()
            messages.success(request, 'Карточка успешно добавлена!')
            return redirect('study_modules:unit_detail', module_id=module_id, unit_id=unit_id)
    else:
        form = UnitTheoryCardForm()
    
    context = {
        'module': module,
        'unit': unit,
        'section': section,
        'form': form,
        'form_type': 'unit_theory_card'
    }
    return render(request, 'study_modules/add_item.html', context)


@login_required
def unit_theory_card_detail(request, module_id, unit_id, section_id, card_id):
    """Детальная страница теоретической карточки юнита с редактором"""
    module = get_object_or_404(StudyModule, pk=module_id)
    unit = get_object_or_404(Unit, pk=unit_id, module=module)
    section = get_object_or_404(UnitSection, pk=section_id, unit=unit)
    card = get_object_or_404(UnitTheoryCard, pk=card_id, section=section)
    
    if request.method == 'POST':
        # Только автор может редактировать
        if module.author != request.user:
            messages.error(request, 'У вас нет прав для редактирования этой карточки.')
            return redirect('study_modules:unit_theory_card_detail', module_id=module_id, unit_id=unit_id, section_id=section_id, card_id=card_id)
        
        content = request.POST.get('content', '')
        card.content = content
        card.save()
        messages.success(request, 'Карточка успешно сохранена!')
        return redirect('study_modules:unit_theory_card_detail', module_id=module_id, unit_id=unit_id, section_id=section_id, card_id=card_id)
    
    context = {
        'module': module,
        'unit': unit,
        'section': section,
        'card': card,
    }
    return render(request, 'study_modules/unit_theory_card_detail.html', context)


@login_required
def edit_unit_theory_card(request, module_id, unit_id, card_id):
    """Редактирование теоретической карточки юнита"""
    module = get_object_or_404(StudyModule, pk=module_id)
    unit = get_object_or_404(Unit, pk=unit_id, module=module)
    card = get_object_or_404(UnitTheoryCard, pk=card_id, section__unit=unit)
    
    if module.author != request.user:
        return JsonResponse({'success': False, 'error': 'У вас нет прав для редактирования этой карточки.'})
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        
        if title:
            card.title = title
            card.content = content
            card.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Название карточки не может быть пустым.'})
    
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса.'})


@login_required
def delete_unit_theory_card(request, module_id, unit_id, card_id):
    """Удаление теоретической карточки юнита"""
    module = get_object_or_404(StudyModule, pk=module_id)
    unit = get_object_or_404(Unit, pk=unit_id, module=module)
    card = get_object_or_404(UnitTheoryCard, pk=card_id, section__unit=unit)
    
    if module.author != request.user:
        return JsonResponse({'success': False, 'error': 'У вас нет прав для удаления этой карточки.'})
    
    if request.method == 'POST':
        card.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса.'})


@login_required
def grammar_practice(request, module_id, unit_id, skill_id):
    """Отображение грамматической практики"""
    module = get_object_or_404(StudyModule, pk=module_id)
    unit = get_object_or_404(Unit, pk=unit_id, module=module)
    skill = get_object_or_404(UnitSkill, pk=skill_id, unit=unit, skill_type='grammar')
    
    # Получаем задания для данного навыка
    tasks = GrammarTask.objects.filter(skill=skill, is_active=True).order_by('order')
    
    context = {
        'module': module,
        'unit': unit,
        'skill': skill,
        'tasks': tasks,
    }
    return render(request, 'study_modules/grammar_practice.html', context)


@login_required
def add_grammar_task(request, module_id, unit_id, skill_id):
    """Добавление задания грамматической практики"""
    module = get_object_or_404(StudyModule, pk=module_id)
    unit = get_object_or_404(Unit, pk=unit_id, module=module)
    skill = get_object_or_404(UnitSkill, pk=skill_id, unit=unit, skill_type='grammar')
    
    if module.author != request.user:
        messages.error(request, 'У вас нет прав для добавления заданий.')
        return redirect('study_modules:grammar_practice', module_id=module_id, unit_id=unit_id, skill_id=skill_id)
    
    if request.method == 'POST':
        form = GrammarTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.skill = skill
            
            # Обрабатываем простые поля и создаем JSON
            task_type = request.POST.get('task_type')
            
            if task_type == 'matching':
                left_words = request.POST.get('left_words', '').strip().split('\n')
                right_words = request.POST.get('right_words', '').strip().split('\n')
                
                left_items = [{'id': str(i+1), 'text': word.strip()} for i, word in enumerate(left_words) if word.strip()]
                right_items = [{'id': str(i+1), 'text': word.strip()} for i, word in enumerate(right_words) if word.strip()]
                
                task.content = {
                    'left_items': left_items,
                    'right_items': right_items
                }
                task.correct_answer = {'matching': 'correct'}  # Для соединения слов проверка идет по ID
                
            elif task_type == 'sentence_rewrite':
                example = request.POST.get('sentence_example', '').strip()
                answer = request.POST.get('sentence_answer', '').strip()
                
                task.content = {'example': example}
                task.correct_answer = {'answer': answer}
                
            elif task_type == 'translation_choice':
                sentence = request.POST.get('english_sentence', '').strip()
                options_text = request.POST.get('translation_options', '').strip()
                
                options = []
                for i, option_text in enumerate(options_text.split('\n')):
                    if option_text.strip():
                        is_correct = option_text.strip().startswith('*')
                        text = option_text.strip().lstrip('*').strip()
                        options.append({
                            'text': text,
                            'correct': is_correct
                        })
                
                task.content = {
                    'sentence': sentence,
                    'options': options
                }
                task.correct_answer = {'choice': 'correct'}
                
            elif task_type == 'sentence_builder':
                words_text = request.POST.get('sentence_words', '').strip()
                correct_sentence = request.POST.get('correct_sentence', '').strip()
                
                words = [word.strip() for word in words_text.split(',') if word.strip()]
                
                task.content = {'words': words}
                task.correct_answer = {'sentence': correct_sentence}
            
            # Задание всегда активно
            task.is_active = True
            
            task.save()
            messages.success(request, 'Задание успешно добавлено!')
            return redirect('study_modules:grammar_practice', module_id=module_id, unit_id=unit_id, skill_id=skill_id)
    else:
        form = GrammarTaskForm()
    
    context = {
        'module': module,
        'unit': unit,
        'skill': skill,
        'form': form,
        'form_type': 'grammar_task'
    }
    return render(request, 'study_modules/add_item.html', context)


@login_required
def edit_grammar_task(request, module_id, unit_id, skill_id, task_id):
    """Редактирование задания грамматической практики"""
    module = get_object_or_404(StudyModule, pk=module_id)
    unit = get_object_or_404(Unit, pk=unit_id, module=module)
    skill = get_object_or_404(UnitSkill, pk=skill_id, unit=unit, skill_type='grammar')
    task = get_object_or_404(GrammarTask, pk=task_id, skill=skill)
    
    if module.author != request.user:
        return JsonResponse({'success': False, 'error': 'У вас нет прав для редактирования этого задания.'})
    
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.instruction = data.get('instruction', task.instruction)
        task.content = data.get('content', task.content)
        task.correct_answer = data.get('correct_answer', task.correct_answer)
        task.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса.'})


@login_required
def delete_grammar_task(request, module_id, unit_id, skill_id, task_id):
    """Удаление задания грамматической практики"""
    module = get_object_or_404(StudyModule, pk=module_id)
    unit = get_object_or_404(Unit, pk=unit_id, module=module)
    skill = get_object_or_404(UnitSkill, pk=skill_id, unit=unit, skill_type='grammar')
    task = get_object_or_404(GrammarTask, pk=task_id, skill=skill)
    
    if module.author != request.user:
        return JsonResponse({'success': False, 'error': 'У вас нет прав для удаления этого задания.'})
    
    if request.method == 'POST':
        task.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса.'})
