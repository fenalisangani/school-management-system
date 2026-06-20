(function () {
    'use strict';

    /* Sidebar mobile toggle */
    var sidebar = document.getElementById('sidebar');
    var toggle = document.getElementById('sidebarToggle');
    var overlay = document.getElementById('sidebarOverlay');

    function closeSidebar() {
        if (sidebar) sidebar.classList.remove('open');
        if (overlay) {
            overlay.classList.remove('visible');
            overlay.setAttribute('aria-hidden', 'true');
        }
    }

    function openSidebar() {
        if (sidebar) sidebar.classList.add('open');
        if (overlay) {
            overlay.classList.add('visible');
            overlay.setAttribute('aria-hidden', 'false');
        }
    }

    if (toggle) {
        toggle.addEventListener('click', function () {
            if (sidebar && sidebar.classList.contains('open')) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
    }

    if (overlay) {
        overlay.addEventListener('click', closeSidebar);
    }

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeSidebar();
    });

    /* Live clock in header (IST via browser locale en-IN) */
    var timeEl = document.getElementById('headerTime');
    var dateEl = document.getElementById('headerDate');

    function updateClock() {
        var now = new Date();
        if (timeEl) {
            timeEl.textContent = now.toLocaleTimeString('en-IN', {
                hour: '2-digit',
                minute: '2-digit',
                hour12: true,
            });
        }
        if (dateEl) {
            dateEl.textContent = now.toLocaleDateString('en-IN', {
                weekday: 'short',
                day: 'numeric',
                month: 'short',
                year: 'numeric',
            });
        }
    }

    updateClock();
    setInterval(updateClock, 30000);

    /* Close the header account dropdown when clicking outside or pressing Escape */
    var userMenu = document.querySelector('.header-user-menu');
    if (userMenu) {
        document.addEventListener('click', function (e) {
            if (userMenu.open && !userMenu.contains(e.target)) {
                userMenu.removeAttribute('open');
            }
        });
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') userMenu.removeAttribute('open');
        });
    }

    /* Toast auto-dismiss */
    var toasts = document.querySelectorAll('.toast');
    toasts.forEach(function (el, i) {
        setTimeout(function () {
            el.style.opacity = '0';
            el.style.transform = 'translateX(20px)';
            el.style.transition = 'opacity 0.4s, transform 0.4s';
            setTimeout(function () { el.remove(); }, 400);
        }, 4500 + i * 300);
    });
})();
