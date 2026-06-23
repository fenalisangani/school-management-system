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

    /* Animated stat counters */
    function animateCount(el, target, duration) {
        var start = 0;
        var startTime = null;
        var isFloat = String(target).indexOf('.') !== -1;

        function step(timestamp) {
            if (!startTime) startTime = timestamp;
            var progress = Math.min((timestamp - startTime) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            var value = start + (target - start) * eased;

            if (isFloat) {
                el.textContent = value.toFixed(1);
            } else {
                el.textContent = Math.round(value).toLocaleString('en-IN');
            }

            if (progress < 1) {
                window.requestAnimationFrame(step);
            } else if (isFloat) {
                el.textContent = target.toFixed(1);
            } else {
                el.textContent = Math.round(target).toLocaleString('en-IN');
            }
        }

        window.requestAnimationFrame(step);
    }

    var counters = document.querySelectorAll('[data-count]');
    if (counters.length && 'IntersectionObserver' in window) {
        var counterObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                var el = entry.target;
                if (el.dataset.animated) return;
                el.dataset.animated = 'true';
                var raw = el.getAttribute('data-count');
                var target = parseFloat(raw);
                if (isNaN(target)) return;
                animateCount(el, target, 900);
                counterObserver.unobserve(el);
            });
        }, { threshold: 0.3 });

        counters.forEach(function (el) {
            counterObserver.observe(el);
        });
    }
})();
