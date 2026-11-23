/**
 * JEJAK TUMBUH — POSYANDU DIGITAL
 * Sistem Notifikasi Toast 5 Detik Anti-Menumpuk
 * Aturan:
 * 1. Notifikasi hanya muncul selama 5 detik
 * 2. Hilang otomatis setelah 5 detik
 * 3. Notifikasi tidak boleh menumpuk (replace previous toast)
 * 4. Animasi transisi smooth (fade in & fade out)
 */

(function () {
  'use strict';

  var toastTimer = null;

  window.showToast = function (message, type) {
    type = ['success', 'danger', 'error', 'warning', 'amber', 'info'].indexOf(type) >= 0 ? type : 'success';
    var container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    // Bersihkan timer dan toast sebelumnya agar TIDAK MENUMPUK
    if (toastTimer) {
      clearTimeout(toastTimer);
      toastTimer = null;
    }
    container.innerHTML = '';

    var toast = document.createElement('div');
    toast.className = 'toast-item toast-' + type + ' animate-toast-in';

    var iconClass = 'fa-check-circle';
    if (type === 'danger' || type === 'error') iconClass = 'fa-exclamation-circle';
    if (type === 'warning' || type === 'amber') iconClass = 'fa-triangle-exclamation';
    if (type === 'info') iconClass = 'fa-info-circle';

    toast.innerHTML = '<div class="toast-content"><i class="fas ' + iconClass + ' toast-icon"></i>' +
      '<div class="toast-text"></div></div>' +
      '<button class="toast-close" type="button" aria-label="Tutup">&times;</button>' +
      '<div class="toast-progress"><div class="toast-progress-bar"></div></div>';
    toast.querySelector('.toast-text').textContent = String(message == null ? '' : message);
    toast.querySelector('.toast-close').addEventListener('click', window.dismissToast);

    container.appendChild(toast);

    // Auto dismiss dalam 5 detik (5000ms)
    toastTimer = setTimeout(function () {
      window.dismissToast();
    }, 5000);
  };

  window.dismissToast = function () {
    var container = document.getElementById('toast-container');
    if (!container) return;
    var toast = container.querySelector('.toast-item');
    if (toast) {
      toast.classList.remove('animate-toast-in');
      toast.classList.add('animate-toast-out');
      setTimeout(function () {
        if (container.contains(toast)) {
          container.removeChild(toast);
        }
      }, 320);
    }
    if (toastTimer) {
      clearTimeout(toastTimer);
      toastTimer = null;
    }
  };

  // Otomatis tangkap flash message di DOM saat halaman dimuat
  document.addEventListener('DOMContentLoaded', function () {
    var flashDataEl = document.getElementById('server-flash-data');
    if (flashDataEl) {
      try {
        var flashData = JSON.parse(flashDataEl.textContent);
        if (flashData && flashData.length > 0) {
          // Tampilkan pesan pertama (anti-menumpuk)
          var lastMsg = flashData[flashData.length - 1];
          window.showToast(lastMsg[1], lastMsg[0]);
        }
      } catch (e) {
        console.error('Error parsing flash data:', e);
      }
    }
  });

})();
