let currentStep = 1;
let timerInterval;
let timeRemaining = 10;

function updateProgress() {
  document.querySelectorAll('.circle').forEach((circle, index) => {
    circle.classList.toggle('active', index < currentStep);
  });

  document.querySelectorAll('.step').forEach(step => {
    step.classList.add('hidden');
  });
  document.getElementById(`form-step-${currentStep}`).classList.remove('hidden');
}

function nextStep() {
  if (currentStep < 3) {
    currentStep++;
    updateProgress();
    if (currentStep === 3) startTimer();
  }
}

function prevStep() {
  if (currentStep > 1) {
    currentStep--;
    updateProgress();
  }
}

function startTimer() {
  const timerElement = document.getElementById('timer');
  timerElement.textContent = timeRemaining;

  timerInterval = setInterval(() => {
    timeRemaining--;
    timerElement.textContent = timeRemaining;

    if (timeRemaining <= 0) {
      clearInterval(timerInterval);
      document.getElementById('timer-container').style.display = 'none';
      document.getElementById('resend-btn').style.display = 'block';
    }
  }, 1000);
}

function resendCode() {
  timeRemaining = 10;
  document.getElementById('resend-btn').style.display = 'none';
  document.getElementById('timer-container').style.display = 'flex';
  startTimer();
}

// Функции для работы с ролями
function selectRole(role) {
  const roleCards = document.querySelectorAll('.role-card');
  const roleInput = document.getElementById('selected_role');
  
  roleCards.forEach(card => {
    const isActive = card.getAttribute('data-role') === role;
    card.classList.toggle('active', isActive);
  });
  
  if (roleInput) roleInput.value = role;
}

// Валидация шагов
function validateStep(step) {
  const inputs = document.querySelectorAll(`#form-step-${step} input:required`);
  const roleInput = document.getElementById('selected_role');
  let isValid = true;

  inputs.forEach(input => {
    if (!input.value.trim()) {
      input.classList.add('error');
      isValid = false;
    } else {
      input.classList.remove('error');
    }
  });

  // Проверка выбора роли на шаге 2
  if (step === 2 && roleInput && !roleInput.value) {
    isValid = false;
    const roleCards = document.querySelectorAll('.role-card');
    roleCards.forEach(card => {
      card.style.transform = 'translateY(-8px) scale(1.02)';
      setTimeout(() => { card.style.transform = ''; }, 150);
    });
  }

  if (isValid) nextStep();
}

