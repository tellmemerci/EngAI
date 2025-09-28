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

// Валидация шагов
function validateStep(step) {
  const inputs = document.querySelectorAll(`#form-step-${step} input:required`);
  let isValid = true;

  inputs.forEach(input => {
    if (!input.value.trim()) {
      input.classList.add('error');
      isValid = false;
    } else {
      input.classList.remove('error');
    }
  });

  if (isValid) nextStep();
}

