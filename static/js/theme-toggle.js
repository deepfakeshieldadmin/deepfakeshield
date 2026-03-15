/* ═══════════════════════════════════════════════════════════════
   DeepFake Shield — Theme Toggle (Dark / Light)
   Persists preference in localStorage
   Syncs with system preference if no saved preference
   ═══════════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    var STORAGE_KEY = 'dfs_theme';
    var DARK = 'dark';
    var LIGHT = 'light';

    /* ─────────────────────────────────────────────
       Get Preferred Theme
       ───────────────────────────────────────────── */
    function getPreferredTheme() {
        var saved = localStorage.getItem(STORAGE_KEY);
        if (saved === DARK || saved === LIGHT) {
            return saved;
        }

        // Check system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
            return LIGHT;
        }

        return DARK; // Default
    }

    /* ─────────────────────────────────────────────
       Apply Theme
       ───────────────────────────────────────────── */
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(STORAGE_KEY, theme);

        // Update meta theme color
        var meta = document.querySelector('meta[name="theme-color"]');
        if (meta) {
            meta.setAttribute('content', theme === DARK ? '#0a0e27' : '#f7f8fc');
        }

        // Dispatch custom event for other components
        window.dispatchEvent(new CustomEvent('themechange', { detail: { theme: theme } }));
    }

    /* ─────────────────────────────────────────────
       Initialize Theme (runs before DOM ready for no flash)
       ───────────────────────────────────────────── */
    var initialTheme = getPreferredTheme();
    applyTheme(initialTheme);

    /* ─────────────────────────────────────────────
       Toggle Button Setup (after DOM ready)
       ───────────────────────────────────────────── */
    document.addEventListener('DOMContentLoaded', function () {
        var toggleBtn = document.getElementById('theme-toggle');
        if (!toggleBtn) return;

        toggleBtn.addEventListener('click', function () {
            var current = document.documentElement.getAttribute('data-theme');
            var next = current === DARK ? LIGHT : DARK;
            applyTheme(next);

            // Add a small transition animation to the body
            document.body.style.transition = 'background-color 0.4s ease, color 0.4s ease';
            setTimeout(function () {
                document.body.style.transition = '';
            }, 500);

            // Reinitialize AOS for new theme
            if (typeof AOS !== 'undefined') {
                setTimeout(function () {
                    AOS.refresh();
                }, 100);
            }
        });

        // Listen for system theme changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
                // Only change if user hasn't manually set preference
                var saved = localStorage.getItem(STORAGE_KEY);
                if (!saved) {
                    applyTheme(e.matches ? DARK : LIGHT);
                }
            });
        }
    });

})();