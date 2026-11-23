/**
 * JEJAK TUMBUH — POSYANDU DIGITAL
 * Landing Page 3-Step Navigation & Demo Account Auto-Fill
 */

(function () {
  'use strict';

  var currentStep = 1;

  window.goToStep = function (step) {
    if (step < 1 || step > 3) return;
    currentStep = step;

    // Update Steps display
    for (var i = 1; i <= 3; i++) {
      var stepEl = document.getElementById('step-' + i);
      var pillEl = document.getElementById('stepper-pill-' + i);
      if (stepEl) {
        if (i === step) {
          stepEl.classList.add('active');
        } else {
          stepEl.classList.remove('active');
        }
      }
      if (pillEl) {
        pillEl.classList.remove('active', 'done');
        if (i === step) {
          pillEl.classList.add('active');
        } else if (i < step) {
          pillEl.classList.add('done');
        }
      }
    }

    // Scroll to top of card smoothly
    var card = document.querySelector('.landing-card');
    if (card) {
      card.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  // Auth Tab Switcher (Login vs Register)
  window.switchAuthTab = function (tab) {
    var tabLogin = document.getElementById('tab-btn-login');
    var tabReg = document.getElementById('tab-btn-reg');
    var formLogin = document.getElementById('form-login');
    var formReg = document.getElementById('form-reg');

    if (tab === 'login') {
      if (tabLogin) tabLogin.classList.add('active');
      if (tabReg) tabReg.classList.remove('active');
      if (formLogin) formLogin.style.display = 'block';
      if (formReg) formReg.style.display = 'none';
    } else {
      if (tabLogin) tabLogin.classList.remove('active');
      if (tabReg) tabReg.classList.add('active');
      if (formLogin) formLogin.style.display = 'none';
      if (formReg) formReg.style.display = 'block';
    }
  };

  // Keep the registration form scoped to the selected participant role.
  var registrationRole = document.getElementById('registration-role');
  if (registrationRole) {
    var parentFields = document.getElementById('registration-fields-ortu');
    var pregnancyFields = document.getElementById('registration-fields-ibu');
    var nameLabel = document.getElementById('registration-name-label');

    function updateRegistrationFields() {
      var isPregnant = registrationRole.value === 'Ibu Hamil';
      parentFields.hidden = isPregnant;
      parentFields.disabled = isPregnant;
      pregnancyFields.hidden = !isPregnant;
      pregnancyFields.disabled = !isPregnant;
      nameLabel.textContent = isPregnant ? 'Nama Ibu Hamil *' : 'Nama Orang Tua *';
    }

    registrationRole.addEventListener('change', updateRegistrationFields);
    updateRegistrationFields();
  }

  // 1-Click Demo Account Autofill & Submit
  window.fillDemoAccount = function (emailOrUsername, password, autoSubmit) {
    // Ensure we are in step 3 and login tab
    window.goToStep(3);
    window.switchAuthTab('login');

    var emailInput = document.getElementById('login-email');
    var pwInput = document.getElementById('login-password');
    var submitBtn = document.getElementById('login-submit-btn');

    if (emailInput) {
      emailInput.value = emailOrUsername;
      emailInput.classList.add('animate-fade-in');
    }
    if (pwInput) {
      pwInput.value = password;
      pwInput.classList.add('animate-fade-in');
    }

    if (autoSubmit && submitBtn) {
      submitBtn.click();
    }
  };

})();
