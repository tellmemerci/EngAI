// module_detail.js - JavaScript для интерактивности страницы модуля

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех интерактивных элементов
    initializeSkillCards();
    initializeFileCards();
    initializeAnimations();
    initializeTooltips();
});

// Инициализация карточек навыков
function initializeSkillCards() {
    const skillCards = document.querySelectorAll('.skill-card:not(.disabled)');
    
    skillCards.forEach(card => {
        // Добавляем эффект наведения
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
            this.style.boxShadow = '0 15px 35px rgba(98,0,234,0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 20px rgba(0,0,0,0.08)';
        });
        
        // Добавляем эффект клика
        card.addEventListener('click', function() {
            // Добавляем анимацию клика
            this.style.transform = 'translateY(-4px) scale(0.98)';
            setTimeout(() => {
                this.style.transform = 'translateY(-8px) scale(1)';
            }, 150);
            
            // Получаем тип навыка
            const skillType = this.classList[1];
            navigateToSkill(skillType);
        });
    });
}

// Инициализация карточек файлов
function initializeFileCards() {
    const fileCards = document.querySelectorAll('.file-card');
    
    fileCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 8px 25px rgba(0,0,0,0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 15px rgba(0,0,0,0.05)';
        });
    });
}

// Инициализация анимаций
function initializeAnimations() {
    // Анимация появления карточек
    const skillCards = document.querySelectorAll('.skill-card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 100);
            }
        });
    }, { threshold: 0.1 });
    
    skillCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'all 0.6s ease-out';
        observer.observe(card);
    });
}

// Инициализация подсказок
function initializeTooltips() {
    const skillCards = document.querySelectorAll('.skill-card');
    
    skillCards.forEach(card => {
        const skillType = card.classList[1];
        const tooltipText = getSkillTooltip(skillType);
        
        // Создаем элемент подсказки
        const tooltip = document.createElement('div');
        tooltip.className = 'skill-tooltip';
        tooltip.textContent = tooltipText;
        tooltip.style.cssText = `
            position: absolute;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.9rem;
            white-space: nowrap;
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s;
            top: -40px;
            left: 50%;
            transform: translateX(-50%);
        `;
        
        card.style.position = 'relative';
        card.appendChild(tooltip);
        
        // Показываем подсказку при наведении
        card.addEventListener('mouseenter', function() {
            tooltip.style.opacity = '1';
        });
        
        card.addEventListener('mouseleave', function() {
            tooltip.style.opacity = '0';
        });
    });
}

// Получение текста подсказки для навыка
function getSkillTooltip(skillType) {
    const tooltips = {
        'listening': 'Развитие навыков аудирования',
        'writing': 'Практика письменной речи',
        'grammar': 'Изучение грамматических правил',
        'reading': 'Улучшение навыков чтения',
        'speaking': 'Развитие устной речи',
        'words': 'Расширение словарного запаса',
        'watching': 'Просмотр видео материалов',
        'test': 'Проверка знаний'
    };
    return tooltips[skillType] || 'Навык';
}

// Навигация к навыку
function navigateToSkill(skillType) {
    // Здесь можно добавить логику навигации к конкретному навыку
    console.log('Переход к навыку:', skillType);
    
    // Показываем уведомление
    showNotification(`Переход к навыку: ${getSkillTooltip(skillType)}`, 'info');
    
    // Пример: можно добавить переход на страницу навыка
    // window.location.href = `/modules/${getModuleId()}/skill/${skillType}/`;
}

// Получение ID модуля из URL
function getModuleId() {
    const path = window.location.pathname;
    const matches = path.match(/\/modules\/(\d+)\//);
    return matches ? matches[1] : null;
}

// Показ уведомлений
function showNotification(message, type = 'info') {
    // Создаем элемент уведомления
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Стили для уведомления
    const colors = {
        'info': '#2196f3',
        'success': '#4caf50',
        'warning': '#ff9800',
        'error': '#f44336'
    };
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type] || colors.info};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Анимация появления
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Автоматическое скрытие
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Обработка ошибок
window.addEventListener('error', function(e) {
    console.error('Ошибка:', e.error);
    showNotification('Произошла ошибка. Пожалуйста, обновите страницу.', 'error');
});

// Функция для загрузки контента навыка (AJAX)
function loadSkillContent(skillType) {
    const moduleId = getModuleId();
    if (!moduleId) return;
    
    showNotification('Загрузка контента...', 'info');
    
    fetch(`/modules/${moduleId}/skill/${skillType}/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Ошибка загрузки');
        }
        return response.json();
    })
    .then(data => {
        showNotification('Контент загружен успешно!', 'success');
        // Здесь можно обработать загруженные данные
        console.log('Загруженный контент:', data);
    })
    .catch(error => {
        console.error('Ошибка:', error);
        showNotification('Ошибка загрузки контента', 'error');
    });
}

// Функция для сохранения прогресса
function saveProgress(skillType, progress) {
    const moduleId = getModuleId();
    if (!moduleId) return;
    
    fetch(`/modules/${moduleId}/progress/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            skill_type: skillType,
            progress: progress
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification('Прогресс сохранен!', 'success');
        }
    })
    .catch(error => {
        console.error('Ошибка сохранения прогресса:', error);
    });
}

// Получение CSRF токена
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

// Экспорт функций для использования в других скриптах
window.ModuleDetail = {
    navigateToSkill,
    loadSkillContent,
    saveProgress,
    showNotification
};
