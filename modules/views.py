from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Module, Task, TaskBlock # Импортируем Module, Task, TaskBlock из текущего приложения
from study_modules.models import StudyModule, Unit, Topic # Импортируем StudyModule, Unit, Topic из study_modules
from .forms import TaskForm # Импортируем TaskForm

# Create your views here.

@login_required
def add_task(request, module_id, unit_id, topic_id):
    study_module = get_object_or_404(StudyModule, pk=module_id) # Используем StudyModule из study_modules
    unit = get_object_or_404(Unit, pk=unit_id, module=study_module)
    topic = get_object_or_404(Topic, pk=topic_id, unit=unit)

    if study_module.author != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого модуля.')
        return redirect('study_modules:topic_detail', module_id=module_id, unit_id=unit_id, topic_id=topic_id) # Обновляем redirect

    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.topic = topic
            # Если TaskBlock обязателен, нужно предоставить возможность его выбора или создать по умолчанию
            # Пока что просто берем первый попавшийся TaskBlock, связанный с модулем, если он есть
            # В будущем, здесь должна быть более продуманная логика выбора/создания TaskBlock
            task_block = TaskBlock.objects.filter(module=study_module.id).first()
            if task_block:
                task.task_block = task_block
            else:
                # Если нет TaskBlock, создаем его. Тип пока generic.
                task_block = TaskBlock.objects.create(module_id=study_module.id, type='Other')
                task.task_block = task_block
            task.save()
            messages.success(request, 'Задание успешно добавлено!')
            return redirect('study_modules:topic_detail', module_id=module_id, unit_id=unit_id, topic_id=topic_id) # Обновляем redirect
    else:
        form = TaskForm(initial={'topic': topic})

    context = {
        'module': study_module,
        'unit': unit,
        'topic': topic,
        'form': form,
        'form_type': 'task',
        'title': 'Добавление задания'
    }
    return render(request, 'study_modules/add_item.html', context) # Используем общий шаблон add_item

@login_required
def edit_task(request, module_id, unit_id, topic_id, task_id):
    study_module = get_object_or_404(StudyModule, pk=module_id)
    unit = get_object_or_404(Unit, pk=unit_id, module=study_module)
    topic = get_object_or_404(Topic, pk=topic_id, unit=unit)
    task = get_object_or_404(Task, pk=task_id, topic=topic)

    if study_module.author != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого модуля.')
        return redirect('study_modules:topic_detail', module_id=module_id, unit_id=unit_id, topic_id=topic_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Задание успешно обновлено!')
            return redirect('study_modules:topic_detail', module_id=module_id, unit_id=unit_id, topic_id=topic_id)
    else:
        form = TaskForm(instance=task)

    context = {
        'module': study_module,
        'unit': unit,
        'topic': topic,
        'task': task,
        'form': form,
        'form_type': 'task',
        'title': 'Редактирование задания'
    }
    return render(request, 'study_modules/add_item.html', context)


@login_required
def delete_task(request, module_id, unit_id, topic_id, task_id):
    study_module = get_object_or_404(StudyModule, pk=module_id)
    unit = get_object_or_404(Unit, pk=unit_id, module=study_module)
    topic = get_object_or_404(Topic, pk=topic_id, unit=unit)
    task = get_object_or_404(Task, pk=task_id, topic=topic)

    if study_module.author != request.user:
        messages.error(request, 'У вас нет прав для удаления этого задания.')
        return redirect('study_modules:topic_detail', module_id=module_id, unit_id=unit_id, topic_id=topic_id)

    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Задание успешно удалено!')
        return redirect('study_modules:topic_detail', module_id=module_id, unit_id=unit_id, topic_id=topic_id)

    context = {
        'module': study_module,
        'unit': unit,
        'topic': topic,
        'task': task,
        'title': 'Удаление задания'
    }
    return render(request, 'study_modules/confirm_delete.html', context)
