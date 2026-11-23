/**
 * JEJAK TUMBUH — POSYANDU DIGITAL
 * AutoEDA Hover Sidebar Interaction Engine
 */

(function () {
  'use strict';

  function initSidebar() {
    var sidebar = document.getElementById('sidebar');
    var mobileToggle = document.getElementById('sidebarMobileToggle');
    if (!sidebar) return;

    // Desktop: default collapsed (mini mode)
    if (window.innerWidth > 768) {
      sidebar.classList.add('mini');
    }

    // Auto expand on hover, auto collapse on leave
    var resizeTimer = null;
    function triggerResize() {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () {
        window.dispatchEvent(new Event('resize'));
      }, 290);
    }

    sidebar.addEventListener('mouseenter', function () {
      if (window.innerWidth <= 768) return;
      sidebar.classList.remove('mini');
      triggerResize();
    });

    sidebar.addEventListener('mouseleave', function () {
      if (window.innerWidth <= 768) return;
      sidebar.classList.add('mini');
      triggerResize();
    });

    // Touch / Mobile Toggle
    if (mobileToggle) {
      mobileToggle.addEventListener('click', function (e) {
        e.stopPropagation();
        sidebar.classList.toggle('mobile-open');
      });
    }

    // Close on click outside on mobile
    document.addEventListener('click', function (e) {
      if (window.innerWidth <= 768 && sidebar.classList.contains('mobile-open')) {
        if (!sidebar.contains(e.target) && e.target !== mobileToggle) {
          sidebar.classList.remove('mobile-open');
        }
      }
    });

    // Handle touch device tap to expand
    sidebar.addEventListener('touchstart', function () {
      if (window.innerWidth > 768 && sidebar.classList.contains('mini')) {
        sidebar.classList.remove('mini');
        triggerResize();
      }
    }, { passive: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSidebar);
  } else {
    initSidebar();
  }
})();
