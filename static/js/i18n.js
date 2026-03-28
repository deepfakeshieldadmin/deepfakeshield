/**
 * DeepFake Shield — Custom Translation Widget
 * File: static/js/i18n.js
 * 
 * REPLACES Google Translate widget completely.
 * - No Google logo
 * - No page redirect  
 * - Stays on same page
 * - Uses Google Translate Element API invisibly
 * - Clean dropdown in navbar
 */

(function () {
    'use strict';

    // ── Supported Languages ──
    const LANGUAGES = [
        { code: 'en', name: 'English', flag: '🇬🇧' },
        { code: 'hi', name: 'हिंदी', flag: '🇮🇳' },
        { code: 'ta', name: 'தமிழ்', flag: '🇮🇳' },
        { code: 'te', name: 'తెలుగు', flag: '🇮🇳' },
        { code: 'ml', name: 'മലയാളം', flag: '🇮🇳' },
        { code: 'kn', name: 'ಕನ್ನಡ', flag: '🇮🇳' },
        { code: 'mr', name: 'मराठी', flag: '🇮🇳' },
        { code: 'bn', name: 'বাংলা', flag: '🇧🇩' },
        { code: 'fr', name: 'Français', flag: '🇫🇷' },
        { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
        { code: 'es', name: 'Español', flag: '🇪🇸' },
        { code: 'ar', name: 'العربية', flag: '🇸🇦' },
        { code: 'zh-CN', name: '中文', flag: '🇨🇳' },
        { code: 'ja', name: '日本語', flag: '🇯🇵' },
    ];

    // ── Hidden Google Translate container ──
    function injectGoogleTranslate() {
        // Add hidden container for Google Translate
        const container = document.createElement('div');
        container.id = 'google_translate_element';
        container.style.cssText = 'position:absolute;top:-9999px;left:-9999px;visibility:hidden;';
        document.body.appendChild(container);

        // Hide Google Translate bar that appears at top
        const style = document.createElement('style');
        style.textContent = `
            /* Hide Google Translate bar completely */
            .goog-te-banner-frame,
            .goog-te-balloon-frame,
            #goog-gt-tt,
            .goog-te-balloon-frame,
            .skiptranslate {
                display: none !important;
                visibility: hidden !important;
            }
            body { top: 0 !important; }
            .goog-tooltip { display: none !important; }
            .goog-tooltip:hover { display: none !important; }
            .goog-text-highlight {
                background-color: transparent !important;
                box-shadow: none !important;
            }
            /* Hide Google logo in translate bar */
            .goog-logo-link { display: none !important; }
            .goog-te-gadget { display: none !important; }
        `;
        document.head.appendChild(style);
    }

    // ── Initialize Google Translate API ──
    window.googleTranslateElementInit = function () {
        new google.translate.TranslateElement({
            pageLanguage: 'en',
            includedLanguages: LANGUAGES.map(l => l.code).join(','),
            layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
            autoDisplay: false,
        }, 'google_translate_element');
    };

    // ── Load Google Translate Script ──
    function loadGoogleTranslate() {
        const script = document.createElement('script');
        script.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
        script.async = true;
        document.head.appendChild(script);
    }

    // ── Change Language Function ──
    function changeLanguage(langCode) {
        if (langCode === 'en') {
            // Restore original language
            const cookieName = '/';
            document.cookie = 'googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
            document.cookie = 'googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=' + location.hostname;
            window.location.reload();
            return;
        }

        // Set Google Translate cookie
        const value = `/en/${langCode}`;
        document.cookie = `googtrans=${value}; path=/`;
        document.cookie = `googtrans=${value}; path=/; domain=.${location.hostname}`;

        // Trigger translation using hidden select element
        const select = document.querySelector('.goog-te-combo');
        if (select) {
            select.value = langCode;
            select.dispatchEvent(new Event('change'));
        } else {
            // Fallback: reload with cookie set
            window.location.reload();
        }

        // Save preference
        localStorage.setItem('dfs_language', langCode);
        updateLanguageButton(langCode);
    }

    // ── Update language button display ──
    function updateLanguageButton(langCode) {
        const lang = LANGUAGES.find(l => l.code === langCode) || LANGUAGES[0];
        const btn = document.getElementById('dfs-lang-btn');
        if (btn) {
            btn.innerHTML = `<span class="lang-flag">${lang.flag}</span> <span class="lang-name">${lang.name}</span> <i class="fas fa-chevron-down ms-1" style="font-size:0.7rem;"></i>`;
        }
    }

    // ── Build custom language dropdown ──
    function buildLanguageDropdown() {
        // Find existing language selector containers in navbar
        const existingLangContainers = document.querySelectorAll(
            '.language-selector, [data-language-selector], #language-dropdown, .lang-selector'
        );

        // Build dropdown HTML
        const currentLang = localStorage.getItem('dfs_language') || 'en';
        const currentLangObj = LANGUAGES.find(l => l.code === currentLang) || LANGUAGES[0];

        const dropdownHTML = `
        <div class="dfs-language-dropdown" id="dfs-lang-wrapper" style="position:relative;display:inline-block;">
            <button id="dfs-lang-btn"
                style="background:transparent;border:1px solid rgba(255,255,255,0.2);
                       border-radius:8px;padding:6px 12px;cursor:pointer;
                       color:inherit;display:flex;align-items:center;gap:6px;
                       font-size:0.875rem;transition:all 0.2s;"
                onclick="window.DFSLang.toggleDropdown(event)">
                <span class="lang-flag">${currentLangObj.flag}</span>
                <span class="lang-name">${currentLangObj.name}</span>
                <i class="fas fa-chevron-down ms-1" style="font-size:0.7rem;"></i>
            </button>
            <div id="dfs-lang-menu"
                style="display:none;position:absolute;top:calc(100% + 8px);right:0;
                       background:var(--bg-secondary, #1a1a2e);border:1px solid rgba(255,255,255,0.1);
                       border-radius:10px;padding:8px;min-width:160px;z-index:9999;
                       box-shadow:0 8px 32px rgba(0,0,0,0.3);max-height:320px;overflow-y:auto;">
                ${LANGUAGES.map(lang => `
                    <div class="dfs-lang-item"
                        data-lang="${lang.code}"
                        onclick="window.DFSLang.select('${lang.code}')"
                        style="padding:8px 12px;cursor:pointer;border-radius:6px;
                               display:flex;align-items:center;gap:8px;font-size:0.875rem;
                               transition:background 0.15s;color:inherit;"
                        onmouseover="this.style.background='rgba(255,255,255,0.08)'"
                        onmouseout="this.style.background='transparent'">
                        <span style="font-size:1.1rem;">${lang.flag}</span>
                        <span>${lang.name}</span>
                        ${lang.code === currentLang ? '<i class="fas fa-check ms-auto" style="color:#00d4ff;font-size:0.75rem;"></i>' : ''}
                    </div>
                `).join('')}
            </div>
        </div>`;

        // Replace existing language selectors
        existingLangContainers.forEach(container => {
            container.innerHTML = dropdownHTML;
        });

        // If no existing container found, find the navbar and inject
        if (existingLangContainers.length === 0) {
            // Look for common navbar selectors
            const navbar = document.querySelector(
                '.navbar-nav, nav .d-flex, .nav-right, #navbarNav .d-flex'
            );
            if (navbar) {
                const wrapper = document.createElement('div');
                wrapper.className = 'nav-item dfs-lang-nav-item';
                wrapper.innerHTML = dropdownHTML;
                // Insert before last item (usually user menu/login button)
                const lastItem = navbar.lastElementChild;
                navbar.insertBefore(wrapper, lastItem);
            }
        }
    }

    // ── Close dropdown when clicking outside ──
    document.addEventListener('click', function (e) {
        const wrapper = document.getElementById('dfs-lang-wrapper');
        if (wrapper && !wrapper.contains(e.target)) {
            const menu = document.getElementById('dfs-lang-menu');
            if (menu) menu.style.display = 'none';
        }
    });

    // ── Public API ──
    window.DFSLang = {
        toggleDropdown: function (e) {
            e.stopPropagation();
            const menu = document.getElementById('dfs-lang-menu');
            if (menu) {
                menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
            }
        },
        select: function (langCode) {
            const menu = document.getElementById('dfs-lang-menu');
            if (menu) menu.style.display = 'none';
            changeLanguage(langCode);
        }
    };

    // ── Apply saved language on page load ──
    function applySavedLanguage() {
        const saved = localStorage.getItem('dfs_language');
        if (saved && saved !== 'en') {
            // Check if cookie is set
            const cookies = document.cookie;
            if (!cookies.includes(`googtrans=/en/${saved}`)) {
                document.cookie = `googtrans=/en/${saved}; path=/`;
            }
        }
    }

    // ── Init ──
    document.addEventListener('DOMContentLoaded', function () {
        applySavedLanguage();
        injectGoogleTranslate();
        loadGoogleTranslate();

        // Build dropdown after a short delay to ensure navbar is rendered
        setTimeout(buildLanguageDropdown, 300);

        // Update button to show current language
        const saved = localStorage.getItem('dfs_language') || 'en';
        setTimeout(() => updateLanguageButton(saved), 400);
    });

})();