// Dashboard JavaScript - Интерактивные элементы

// Переменные для работы с дедлайнами
let userDeadlines = [];
let selectedDate = null;

// API конфигурация
const API_BASE_URL = '/deadlines/api';

// Получение CSRF токена
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
           document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
           getCookie('csrftoken');
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', async function() {
    initCalendar();
    initLearningButton();
    initDeadlineModal();
    await loadDeadlines();
    renderCalendar(); // Перерисовываем календарь после загрузки дедлайнов
});

// ===== КАЛЕНДАРЬ =====
let currentDate = new Date();
const monthNames = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
];

function initCalendar() {
    const prevBtn = document.getElementById('prevMonth');
    const nextBtn = document.getElementById('nextMonth');
    
    if (prevBtn && nextBtn) {
        prevBtn.addEventListener('click', async () => {
            currentDate.setMonth(currentDate.getMonth() - 1);
            await loadDeadlines();
            renderCalendar();
        });
        
        nextBtn.addEventListener('click', async () => {
            currentDate.setMonth(currentDate.getMonth() + 1);
            await loadDeadlines();
            renderCalendar();
        });
    }
    
    // Инициализация календаря
    renderCalendar();
}

function renderCalendar() {
    const monthYear = document.getElementById('monthYear');
    const calendarDays = document.getElementById('calendarDays');
    
    if (!monthYear || !calendarDays) return;
    
    // Обновляем заголовок месяца и года
    monthYear.textContent = `${monthNames[currentDate.getMonth()]} ${currentDate.getFullYear()}`;
    
    // Очищаем предыдущие дни
    calendarDays.innerHTML = '';
    
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    // Первый день месяца
    const firstDay = new Date(year, month, 1);
    // Последний день месяца
    const lastDay = new Date(year, month + 1, 0);
    
    // Корректировка для понедельника как первого дня недели
    let startDay = firstDay.getDay();
    startDay = startDay === 0 ? 6 : startDay - 1;
    
    // Дни предыдущего месяца
    const prevMonthLastDay = new Date(year, month, 0).getDate();
    for (let i = startDay - 1; i >= 0; i--) {
        const dayDiv = createDayElement(prevMonthLastDay - i, true);
        calendarDays.appendChild(dayDiv);
    }
    
    // Дни текущего месяца
    for (let day = 1; day <= lastDay.getDate(); day++) {
        const dayDiv = createDayElement(day, false);
        calendarDays.appendChild(dayDiv);
    }
    
    // Дни следующего месяца для заполнения сетки
    const totalCells = calendarDays.children.length;
    const remainingCells = 42 - totalCells; // 6 недель × 7 дней
    for (let day = 1; day <= remainingCells; day++) {
        const dayDiv = createDayElement(day, true);
        calendarDays.appendChild(dayDiv);
    }
}

function createDayElement(day, isOtherMonth) {
    const dayDiv = document.createElement('div');
    dayDiv.className = 'calendar-day';
    
    // Создаём номер дня
    const dayNumber = document.createElement('div');
    dayNumber.textContent = day;
    dayNumber.style.fontWeight = '600';
    dayDiv.appendChild(dayNumber);
    
    if (isOtherMonth) {
        dayDiv.classList.add('other-month');
    }
    
    // Проверяем, является ли день сегодняшним
    const today = new Date();
    if (!isOtherMonth && 
        day === today.getDate() && 
        currentDate.getMonth() === today.getMonth() && 
        currentDate.getFullYear() === today.getFullYear()) {
        dayDiv.classList.add('today');
    }
    
    // Проверяем наличие дедлайнов на этот день
    if (!isOtherMonth) {
        const dayDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
        const dateStr = dayDate.toISOString().split('T')[0];
        const dayDeadlines = userDeadlines.filter(deadline => deadline.date === dateStr);
        
        if (dayDeadlines.length > 0) {
            dayDiv.classList.add('has-deadline');
            
            // Проверяем, есть ли важные дедлайны
            const hasHighPriority = dayDeadlines.some(deadline => deadline.priority === 'high');
            if (hasHighPriority) {
                dayDiv.classList.add('important');
            }
            
            // Добавляем индикатор
            const indicator = document.createElement('div');
            indicator.className = 'deadline-indicator';
            dayDiv.appendChild(indicator);
            
            // Отображаем количество дедлайнов
            if (dayDeadlines.length === 1) {
                const deadlineText = document.createElement('div');
                deadlineText.className = 'deadline-text';
                deadlineText.textContent = dayDeadlines[0].title.substring(0, 8) + (dayDeadlines[0].title.length > 8 ? '...' : '');
                dayDiv.appendChild(deadlineText);
            } else {
                const deadlineText = document.createElement('div');
                deadlineText.className = 'deadline-text';
                deadlineText.textContent = `${dayDeadlines.length} дел`;
                dayDiv.appendChild(deadlineText);
            }
            
            // Устанавливаем подсказку
            const titles = dayDeadlines.map(d => `${d.time} - ${d.title}`).join('\n');
            dayDiv.title = titles;
        }
    }
    
    // Добавляем пример событий (в будущем здесь будут реальные дедлайны)
    if (!isOtherMonth && isExampleEventDay(day)) {
        dayDiv.classList.add('has-event');
        dayDiv.title = getEventTitle(day);
    }
    
    // Обработчик клика
    dayDiv.addEventListener('click', () => {
        if (!isOtherMonth) {
            handleDayClick(day);
        }
    });
    
    return dayDiv;
}

// ===== ТЕСТОВЫЕ ДЕДЛАЙНЫ =====
function hasDeadline(day) {
    // Тестовые дедлайны
    const deadlineDays = [8, 15, 22, 28];
    return deadlineDays.includes(day);
}

function getDeadlineText(day) {
    const deadlines = {
        8: 'Essay',
        15: 'Test',
        22: 'Project',
        28: 'Exam'
    };
    return deadlines[day] || 'Task';
}

function getDeadlineTitle(day) {
    const deadlineTitles = {
        8: 'Дедлайн: Написать эссе по теме "My Future Career"',
        15: 'Дедлайн: Пройти тест по грамматике (Present Perfect)',
        22: 'Дедлайн: Подготовить презентацию о культуре Англии',
        28: 'Дедлайн: Финальный экзамен по модулю'
    };
    return deadlineTitles[day] || 'Дедлайн';
}

function isImportantDeadline(day) {
    // Важные дедлайны (экзамены, финальные тесты)
    const importantDays = [28]; // Финальный экзамен
    return importantDays.includes(day);
}

// Пример функции для демонстрации событий
function isExampleEventDay(day) {
    // Примеры дедлайнов для демонстрации
    const exampleEvents = [5, 12, 18, 25];
    return exampleEvents.includes(day);
}

function getEventTitle(day) {
    const eventTitles = {
        5: 'Урок грамматики',
        12: 'Проверочный тест',
        18: 'Практика разговорной речи',
        25: 'Итоговая проверка'
    };
    return eventTitles[day] || 'Событие';
}

function handleDayClick(day) {
    console.log(`Клик по дню: ${day}`);
    
    // Сохраняем выбранную дату
    selectedDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
    
    // Обновляем отображение выбранной даты
    updateSelectedDateDisplay();
    
    // Обновляем список дедлайнов
    updateDeadlinesList();
    
    // Подсвечиваем выбранный день
    highlightSelectedDay(day);
}

// ===== КНОПКА ОБУЧЕНИЯ =====
function initLearningButton() {
    // Функция уже определена в HTML как onclick="startLearning()"
    window.startLearning = function() {
        // Анимация нажатия
        const btn = document.querySelector('.learning-btn');
        if (btn) {
            btn.style.transform = 'translateY(-1px) scale(0.98)';
            setTimeout(() => {
                btn.style.transform = '';
            }, 150);
        }
        
        console.log('Начинаем обучение!');
        showNotification('Переход к обучению... Скоро добавим этот функционал!');
        
        // Здесь в будущем будет переход к модулю обучения
        // window.location.href = '/learning/';
    };
}

// ===== КАРТОЧКИ БЫСТРЫХ ДЕЙСТВИЙ =====
function initActionCards() {
    const actionCards = document.querySelectorAll('.action-card');
    
    actionCards.forEach((card, index) => {
        card.addEventListener('click', () => {
            handleActionClick(index, card);
        });
        
        // Добавляем эффект ripple при клике
        card.addEventListener('mousedown', (e) => {
            createRipple(e, card);
        });
    });
}

function handleActionClick(index, cardElement) {
    const actions = [
        'Быстрый урок',
        'Словарь',
        'Практика'
    ];
    
    const actionName = actions[index];
    console.log(`Клик по действию: ${actionName}`);
    
    // Анимация клика
    cardElement.style.transform = 'translateX(8px) scale(0.98)';
    setTimeout(() => {
        cardElement.style.transform = '';
    }, 150);
    
    showNotification(`${actionName} - скоро добавим этот функционал!`);
}

// ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====
function createRipple(event, element) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s ease-out;
        pointer-events: none;
        z-index: 1000;
    `;
    
    // Добавляем CSS анимацию если её нет
    if (!document.querySelector('#ripple-style')) {
        const style = document.createElement('style');
        style.id = 'ripple-style';
        style.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(2);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

function showNotification(message) {
    // Создаем уведомление
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #7c4dff, #9c27b0);
        color: white;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 8px 25px rgba(124, 77, 255, 0.3);
        font-size: 0.9rem;
        font-weight: 500;
        z-index: 10000;
        opacity: 0;
        transform: translateX(100px);
        transition: all 0.3s ease;
        max-width: 300px;
    `;
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Показываем уведомление
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Скрываем уведомление
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100px)';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// ===== АНИМАЦИИ ПРИ ЗАГРУЗКЕ =====
function initAnimations() {
    // Добавляем задержки для анимаций
    const leftElements = document.querySelectorAll('.dashboard-left > *');
    const rightElements = document.querySelectorAll('.dashboard-right > *');
    
    leftElements.forEach((el, index) => {
        el.style.animationDelay = `${index * 0.1}s`;
    });
    
    rightElements.forEach((el, index) => {
        el.style.animationDelay = `${index * 0.1}s`;
    });
}

// ===== АДАПТИВНОСТЬ =====
function handleResize() {
    // Перерисовываем календарь при изменении размера окна
    renderCalendar();
}

window.addEventListener('resize', handleResize);

// ===== СТАТИСТИКА (будущий функционал) =====
function updateStats() {
    // Здесь в будущем будет обновление статистики пользователя
    // из API или локального хранилища
    console.log('Обновление статистики...');
}

// ===== УЧИТЕЛЬ (будущий функционал) =====
function initTeacherCard() {
    const teacherCard = document.querySelector('.teacher-card');
    if (teacherCard) {
        teacherCard.addEventListener('click', () => {
            console.log('Клик по карточке учителя');
            showNotification('Персональный ИИ-учитель - скоро добавим этот функционал!');
        });
    }
}

// ===== УПРАВЛЕНИЕ ДЕДЛАЙНАМИ =====
async function loadDeadlines() {
    try {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth() + 1;
        
        const response = await fetch(`${API_BASE_URL}/by_month/?year=${year}&month=${month}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            credentials: 'same-origin'
        });
        
        if (response.ok) {
            userDeadlines = await response.json();
            console.log('Дедлайны загружены:', userDeadlines);
        } else {
            console.error('Ошибка загрузки дедлайнов:', response.statusText);
            userDeadlines = [];
        }
    } catch (error) {
        console.error('Ошибка сети:', error);
        userDeadlines = [];
    }
}

function updateSelectedDateDisplay() {
    const titleEl = document.getElementById('selectedDateTitle');
    const weekdayEl = document.getElementById('selectedWeekday');
    const dateEl = document.getElementById('selectedDate');
    
    if (!selectedDate) return;
    
    const weekdays = ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'];
    const months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                   'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
    
    titleEl.textContent = `${selectedDate.getDate()} ${months[selectedDate.getMonth()]}`;
    weekdayEl.textContent = weekdays[selectedDate.getDay()];
    dateEl.textContent = selectedDate.getDate();
}

function updateDeadlinesList() {
    const deadlinesList = document.getElementById('deadlinesList');
    
    if (!selectedDate) {
        deadlinesList.innerHTML = '<p class="no-deadlines">Выберите дату</p>';
        return;
    }
    
    const dateStr = selectedDate.toISOString().split('T')[0];
    const dayDeadlines = userDeadlines.filter(deadline => deadline.date === dateStr);
    
    if (dayDeadlines.length === 0) {
        deadlinesList.innerHTML = '<p class="no-deadlines">Нет дедлайнов на эту дату</p>';
        return;
    }
    
    deadlinesList.innerHTML = dayDeadlines.map(deadline => `
        <div class="deadline-item priority-${deadline.priority} ${deadline.is_completed ? 'completed' : ''}" style="border-left-color: ${deadline.color}">
            <div class="deadline-header">
                <h4 class="deadline-title">${deadline.title}</h4>
                <span class="deadline-time">${deadline.time}</span>
            </div>
            ${deadline.description ? `<p class="deadline-description">${deadline.description}</p>` : ''}
            <div class="deadline-actions">
                <div class="deadline-checkbox">
                    <input type="checkbox" id="deadline-${deadline.id}" ${deadline.is_completed ? 'checked' : ''} onchange="toggleDeadlineComplete(${deadline.id})">
                    <label for="deadline-${deadline.id}">Выполнено</label>
                </div>
                <div class="action-buttons">
                    <button class="action-btn edit-btn" onclick="editDeadline(${deadline.id})" title="Редактировать">
                        ✏️
                    </button>
                    <button class="action-btn delete-btn" onclick="deleteDeadline(${deadline.id}, '${deadline.title}')" title="Удалить">
                        🗑️
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function highlightSelectedDay(day) {
    // Убираем предыдущие выделения
    document.querySelectorAll('.calendar-day').forEach(el => {
        el.classList.remove('selected');
    });
    
    // Добавляем класс к выбранному дню
    const dayElements = document.querySelectorAll('.calendar-day');
    dayElements.forEach(el => {
        if (el.textContent.trim().startsWith(day.toString()) && !el.classList.contains('other-month')) {
            el.classList.add('selected');
        }
    });
}

// Инициализация модального окна
function initDeadlineModal() {
    const createBtn = document.getElementById('createDeadlineBtn');
    const modal = document.getElementById('deadlineModal');
    const overlay = document.getElementById('modalOverlay');
    const closeBtn = document.getElementById('modalClose');
    const cancelBtn = document.getElementById('cancelBtn');
    const form = document.getElementById('deadlineForm');
    
    // Открытие модального окна
    createBtn.addEventListener('click', () => {
        modal.classList.add('active');
        
        // Если выбрана дата, подставляем её
        if (selectedDate) {
            const dateInput = document.getElementById('deadlineDate');
            dateInput.value = selectedDate.toISOString().split('T')[0];
        }
        
        document.body.style.overflow = 'hidden';
    });
    
    // Закрытие модального окна
    function closeModal() {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        form.reset();
    }
    
    overlay.addEventListener('click', closeModal);
    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    
    // Обработка сохранения формы
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        saveDeadline();
        closeModal();
    });
}

async function saveDeadline() {
    const form = document.getElementById('deadlineForm');
    const formData = new FormData(form);
    
    const newDeadline = {
        title: formData.get('title'),
        description: formData.get('description'),
        date: formData.get('date'),
        time: formData.get('time'),
        priority: formData.get('priority'),
        color: formData.get('color')
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            credentials: 'same-origin',
            body: JSON.stringify(newDeadline)
        });
        
        if (response.ok) {
            const savedDeadline = await response.json();
            
            // Перезагружаем дедлайны для текущего месяца
            await loadDeadlines();
            
            // Обновляем календарь и список
            renderCalendar();
            updateDeadlinesList();
            
            showNotification('Дедлайн успешно создан!');
        } else {
            const errorData = await response.json();
            console.error('Ошибка сохранения:', errorData);
            showNotification('Ошибка при сохранении дедлайна');
        }
    } catch (error) {
        console.error('Ошибка сети:', error);
        showNotification('Ошибка сети. Попробуйте ещё раз');
    }
}

// ===== ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ДЕДЛАЙНОВ =====
let currentEditingDeadline = null;
let currentDeletingDeadlineId = null;

// Переключение статуса выполнения
async function toggleDeadlineComplete(deadlineId) {
    try {
        const response = await fetch(`${API_BASE_URL}/${deadlineId}/toggle_complete/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            credentials: 'same-origin'
        });
        
        if (response.ok) {
            await loadDeadlines();
            renderCalendar();
            updateDeadlinesList();
            showNotification('Статус дедлайна обновлён!');
        } else {
            console.error('Ошибка обновления статуса');
            showNotification('Ошибка обновления статуса');
        }
    } catch (error) {
        console.error('Ошибка сети:', error);
        showNotification('Ошибка сети');
    }
}

// Редактирование дедлайна
function editDeadline(deadlineId) {
    const deadline = userDeadlines.find(d => d.id === deadlineId);
    if (!deadline) return;
    
    currentEditingDeadline = deadline;
    
    // Заполняем форму редактирования
    document.getElementById('editDeadlineTitle').value = deadline.title;
    document.getElementById('editDeadlineDescription').value = deadline.description || '';
    document.getElementById('editDeadlineDate').value = deadline.date;
    document.getElementById('editDeadlineTime').value = deadline.time;
    document.getElementById('editDeadlinePriority').value = deadline.priority;
    
    // Устанавливаем цвет
    const colorInput = document.querySelector(`input[name="color"][value="${deadline.color}"]`);
    if (colorInput) {
        colorInput.checked = true;
    }
    
    // Открываем модальное окно
    const editModal = document.getElementById('editDeadlineModal');
    editModal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

// Удаление дедлайна
function deleteDeadline(deadlineId, deadlineTitle) {
    currentDeletingDeadlineId = deadlineId;
    
    // Устанавливаем название дедлайна
    document.getElementById('deleteDeadlineTitle').textContent = deadlineTitle;
    
    // Открываем модальное окно подтверждения
    const deleteModal = document.getElementById('deleteConfirmModal');
    deleteModal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

// Подтверждение удаления
async function confirmDelete() {
    if (!currentDeletingDeadlineId) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/${currentDeletingDeadlineId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCSRFToken(),
            },
            credentials: 'same-origin'
        });
        
        if (response.ok) {
            await loadDeadlines();
            renderCalendar();
            updateDeadlinesList();
            showNotification('Дедлайн успешно удалён!');
            
            // Закрываем модальное окно
            const deleteModal = document.getElementById('deleteConfirmModal');
            deleteModal.classList.remove('active');
            document.body.style.overflow = '';
        } else {
            console.error('Ошибка удаления');
            showNotification('Ошибка при удалении дедлайна');
        }
    } catch (error) {
        console.error('Ошибка сети:', error);
        showNotification('Ошибка сети');
    }
    
    currentDeletingDeadlineId = null;
}

// Сохранение изменений дедлайна
async function saveDeadlineChanges() {
    if (!currentEditingDeadline) return;
    
    const form = document.getElementById('editDeadlineForm');
    const formData = new FormData(form);
    
    const updatedDeadline = {
        title: formData.get('title'),
        description: formData.get('description'),
        date: formData.get('date'),
        time: formData.get('time'),
        priority: formData.get('priority'),
        color: formData.get('color')
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/${currentEditingDeadline.id}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            credentials: 'same-origin',
            body: JSON.stringify(updatedDeadline)
        });
        
        if (response.ok) {
            await loadDeadlines();
            renderCalendar();
            updateDeadlinesList();
            showNotification('Дедлайн успешно обновлён!');
            
            // Закрываем модальное окно
            const editModal = document.getElementById('editDeadlineModal');
            editModal.classList.remove('active');
            document.body.style.overflow = '';
            form.reset();
        } else {
            const errorData = await response.json();
            console.error('Ошибка обновления:', errorData);
            showNotification('Ошибка при обновлении дедлайна');
        }
    } catch (error) {
        console.error('Ошибка сети:', error);
        showNotification('Ошибка сети');
    }
    
    currentEditingDeadline = null;
}

// Инициализация модального окна редактирования
function initEditModal() {
    const editModal = document.getElementById('editDeadlineModal');
    const editOverlay = document.getElementById('editModalOverlay');
    const editCloseBtn = document.getElementById('editModalClose');
    const editCancelBtn = document.getElementById('editCancelBtn');
    const editForm = document.getElementById('editDeadlineForm');
    
    function closeEditModal() {
        editModal.classList.remove('active');
        document.body.style.overflow = '';
        editForm.reset();
        currentEditingDeadline = null;
    }
    
    editOverlay.addEventListener('click', closeEditModal);
    editCloseBtn.addEventListener('click', closeEditModal);
    editCancelBtn.addEventListener('click', closeEditModal);
    
    editForm.addEventListener('submit', (e) => {
        e.preventDefault();
        saveDeadlineChanges();
    });
}

// Инициализация модального окна удаления
function initDeleteModal() {
    const deleteModal = document.getElementById('deleteConfirmModal');
    const deleteOverlay = document.getElementById('deleteModalOverlay');
    const deleteCloseBtn = document.getElementById('deleteModalClose');
    const deleteCancelBtn = document.getElementById('deleteCancelBtn');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    
    function closeDeleteModal() {
        deleteModal.classList.remove('active');
        document.body.style.overflow = '';
        currentDeletingDeadlineId = null;
    }
    
    deleteOverlay.addEventListener('click', closeDeleteModal);
    deleteCloseBtn.addEventListener('click', closeDeleteModal);
    deleteCancelBtn.addEventListener('click', closeDeleteModal);
    
    confirmDeleteBtn.addEventListener('click', confirmDelete);
}

// Инициализируем дополнительные элементы
document.addEventListener('DOMContentLoaded', function() {
    initAnimations();
    initTeacherCard();
    initEditModal();
    initDeleteModal();
    
    // Обновляем статистику (в будущем будет реальная)
    setTimeout(updateStats, 1000);
});
