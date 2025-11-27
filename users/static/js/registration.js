document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.registration-form');
    const steps = form.querySelectorAll('.step');
    const progressCircles = document.querySelectorAll('.circle');
    const nextButtons = form.querySelectorAll('.next-step');
    const prevButtons = form.querySelectorAll('.prev-step');
    const finishButton = document.querySelector('.finish-step');
    const resendButton = document.getElementById('resend-btn');
    const timerContainer = document.getElementById('timer-container');
    const hourglass = document.getElementById('hourglass');
    const timerText = document.getElementById('timer-text');

    let currentStep = 0;
    let timerInterval;

    // Функция для показа текущего шага
    function showStep(stepIndex) {
        steps.forEach((step, index) => {
            step.classList.toggle('hidden', index !== stepIndex);
        });

        progressCircles.forEach((circle, index) => {
            circle.classList.toggle('active', index <= stepIndex);
        });

        currentStep = stepIndex;
    }

    // Обработчики для кнопок "Далее"
    nextButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            if (validateStep(currentStep)) {
                form.submit();
            }
        });
    });

    // Обработчики для кнопок "Назад"
    prevButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            showStep(currentStep - 1);
        });
    });

    // Обработчик для кнопки "Завершить"
    if (finishButton) {
        finishButton.addEventListener('click', function(e) {
            e.preventDefault();
            if (validateStep(currentStep)) {
                form.submit();
            }
        });
    }

    // Выбор роли (иконки/карточки)
    const roleCards = document.querySelectorAll('.role-card');
    const roleInput = document.getElementById('selected_role');

    function setRoleActive(role) {
        roleCards.forEach(card => {
            const isActive = card.getAttribute('data-role') === role;
            card.classList.toggle('active', isActive);
        });
        if (roleInput) roleInput.value = role;
    }

    window.selectRole = function(role) {
        setRoleActive(role);
    }

    roleCards.forEach(card => {
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const role = card.getAttribute('data-role');
                setRoleActive(role);
            }
        });
        card.setAttribute('tabindex', '0');
        card.setAttribute('role', 'button');
        card.setAttribute('aria-pressed', 'false');
    });

    // Функция валидации шага
    function validateStep(stepIndex) {
        const currentStepElement = steps[stepIndex];
        const inputs = currentStepElement.querySelectorAll('input[required], select[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('error');
                isValid = false;
            } else {
                input.classList.remove('error');
            }
        });

        // Дополнительная валидация для email и паролей на шаге 1
        if (stepIndex === 0) {
            const emailInput = currentStepElement.querySelector('input[type="email"]');
            if (emailInput && !isValidEmail(emailInput.value)) {
                emailInput.classList.add('error');
                isValid = false;
            }

            const password1 = currentStepElement.querySelector('input[name="password1"], input[name="password"]');
            const password2 = currentStepElement.querySelector('input[name="password2"], input[name="confirm_password"]');
            if (password1 && password2 && password1.value !== password2.value) {
                password1.classList.add('error');
                password2.classList.add('error');
                isValid = false;
            }

            if (password1 && password1.value.length < 8) {
                password1.classList.add('error');
                isValid = false;
            }
        }

        // Проверка выбора роли на шаге 2
        if (stepIndex === 1) {
            const roleSelection = currentStepElement.querySelector('.role-selection');
            
            if (roleInput && !roleInput.value) {
                isValid = false;
                
                // Показать ошибку валидации
                if (roleSelection) {
                    roleSelection.classList.add('error');
                    setTimeout(() => {
                        roleSelection.classList.remove('error');
                    }, 3000);
                }
                
                // Эффект вибрации карточек
                roleCards.forEach((card, index) => {
                    setTimeout(() => {
                        card.style.transform = 'translateY(-8px) scale(1.02)';
                        card.style.borderColor = '#ff5252';
                        setTimeout(() => { 
                            card.style.transform = ''; 
                            card.style.borderColor = ''; 
                        }, 300);
                    }, index * 100);
                });
            } else {
                // Убрать ошибку при валидном выборе
                if (roleSelection) {
                    roleSelection.classList.remove('error');
                }
            }
        }

        return isValid;
    }

    // Функция проверки email
    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    // Функция для таймера
    function startTimer(duration) {
        let timer = duration;
        if (!timerContainer || !resendButton) return;
        timerContainer.style.display = 'flex';
        resendButton.style.display = 'none';

        clearInterval(timerInterval);
        timerInterval = setInterval(function() {
            const minutes = parseInt(timer / 60, 10);
            const seconds = parseInt(timer % 60, 10);

            if (timerText) {
                timerText.textContent = minutes.toString().padStart(2, '0') + ':' + 
                                  seconds.toString().padStart(2, '0');
            }

            if (--timer < 0) {
                clearInterval(timerInterval);
                timerContainer.style.display = 'none';
                resendButton.style.display = 'block';
            }
        }, 1000);
    }

    // Обработчик для кнопки повторной отправки кода
    if (resendButton) {
        resendButton.addEventListener('click', function(e) {
            e.preventDefault();
            fetch('/users/resend-code/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    startTimer(120);
                }
            })
            .catch(() => {});
        });
    }

    // Инициализация таймера при загрузке страницы
    if (timerContainer) {
        startTimer(120);
    }

    // Инициализация телефонного поля
    if (typeof intlTelInput !== 'undefined') {
        const phoneInput = document.querySelector('input[type="tel"]');
        if (phoneInput) {
            intlTelInput(phoneInput, {
                utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js",
                separateDialCode: true,
                initialCountry: "ru"
            });
        }
    }
}); 
