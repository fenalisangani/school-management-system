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

    /* Dashboard stat cards — clickable even on legacy article markup */
    function bindStatCardNavigation(card, href) {
        if (!href || card.dataset.navBound) return;
        card.dataset.navBound = 'true';
        card.classList.add('stat-card-link');
        card.style.cursor = 'pointer';
        card.setAttribute('role', 'link');
        card.setAttribute('tabindex', '0');
        card.addEventListener('click', function (e) {
            if (e.defaultPrevented) return;
            window.location.assign(href);
        });
        card.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                window.location.assign(href);
            }
        });
    }

    function hrefForStatLabel(label, index) {
        var text = (label || '').trim().toLowerCase();
        if (text.indexOf('class') !== -1 || text.indexOf('course') !== -1) return '/classes/';
        if (text.indexOf('student') !== -1) return '/students/';
        if (text.indexOf('teacher') !== -1) return '/teachers/';
        if (text.indexOf('fee') !== -1) return '/fees/assignments/';
        return ['/classes/', '/students/', '/teachers/', '/fees/assignments/'][index] || null;
    }

    document.querySelectorAll('.stats-grid .stat-card, .stats-grid-pro .stat-card, .stats-grid-pro a.stat-card').forEach(function (card, index) {
        if (card.tagName === 'A') {
            var existing = card.getAttribute('href');
            if (existing) return;
        }
        var labelEl = card.querySelector('.stat-label');
        var href = hrefForStatLabel(labelEl ? labelEl.textContent : '', index);
        bindStatCardNavigation(card, href);
    });

    document.querySelectorAll('.hero-metric-card:not(a)').forEach(function (card, index) {
        var href = index === 0 ? '/attendance/students/' : '/attendance/reports/';
        bindStatCardNavigation(card, href);
    });
})();
