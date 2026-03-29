/**
 * DeepFake Shield — i18n.js v3.0
 * Full-page inline translation. No Google logo. No redirect. No new tab.
 * Uses Google Translate Element API invisibly in background.
 */
(function () {
    'use strict';

    const LANGUAGES = [
        { code: 'en',    name: 'English',    flag: '🇬🇧' },
        { code: 'hi',    name: 'हिंदी',       flag: '🇮🇳' },
        { code: 'ta',    name: 'தமிழ்',       flag: '🇮🇳' },
        { code: 'te',    name: 'తెలుగు',      flag: '🇮🇳' },
        { code: 'ml',    name: 'മലയാളം',     flag: '🇮🇳' },
        { code: 'kn',    name: 'ಕನ್ನಡ',      flag: '🇮🇳' },
        { code: 'mr',    name: 'मराठी',       flag: '🇮🇳' },
        { code: 'bn',    name: 'বাংলা',       flag: '🇧🇩' },
        { code: 'fr',    name: 'Français',    flag: '🇫🇷' },
        { code: 'de',    name: 'Deutsch',     flag: '🇩🇪' },
        { code: 'es',    name: 'Español',     flag: '🇪🇸' },
        { code: 'ar',    name: 'العربية',     flag: '🇸🇦' },
        { code: 'zh-CN', name: '中文',         flag: '🇨🇳' },
        { code: 'ja',    name: '日本語',       flag: '🇯🇵' },
    ];

    function injectHideStyles() {
        const s = document.createElement('style');
        s.textContent = `
            .goog-te-banner-frame,.goog-te-balloon-frame,.goog-te-menu-frame,
            #goog-gt-tt,.skiptranslate,.goog-te-gadget,.goog-logo-link,
            iframe.skiptranslate { display:none!important; visibility:hidden!important; }
            body { top:0!important; }
            .goog-tooltip,.goog-tooltip:hover { display:none!important; }
            .goog-text-highlight { background:none!important; box-shadow:none!important; }
        `;
        document.head.appendChild(s);
    }

    function injectGTContainer() {
        if (document.getElementById('google_translate_element')) return;
        const d = document.createElement('div');
        d.id = 'google_translate_element';
        d.style.cssText = 'position:fixed;top:-9999px;left:-9999px;width:1px;height:1px;overflow:hidden;';
        document.body.appendChild(d);
    }

    window.googleTranslateElementInit = function () {
        try {
            new google.translate.TranslateElement({
                pageLanguage: 'en',
                includedLanguages: LANGUAGES.map(l => l.code).join(','),
                layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
                autoDisplay: false,
            }, 'google_translate_element');
        } catch(e) {}
    };

    function loadGT() {
        if (document.getElementById('gt-script')) return;
        const scr = document.createElement('script');
        scr.id = 'gt-script';
        scr.src = 'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
        scr.async = true;
        document.head.appendChild(scr);
    }

    function applyLanguage(code) {
        if (code === 'en') {
            document.cookie = 'googtrans=; expires=Thu,01 Jan 1970 00:00:00 UTC; path=/;';
            document.cookie = `googtrans=; expires=Thu,01 Jan 1970 00:00:00 UTC; path=/; domain=.${location.hostname}`;
            localStorage.removeItem('dfs_lang');
            location.reload();
            return;
        }
        const val = `/en/${code}`;
        document.cookie = `googtrans=${val}; path=/`;
        document.cookie = `googtrans=${val}; path=/; domain=.${location.hostname}`;
        localStorage.setItem('dfs_lang', code);

        const trySelect = (n) => {
            const sel = document.querySelector('.goog-te-combo');
            if (sel) {
                sel.value = code;
                sel.dispatchEvent(new Event('change'));
                updateDropdowns(code);
            } else if (n > 0) {
                setTimeout(() => trySelect(n - 1), 400);
            } else {
                location.reload();
            }
        };
        trySelect(12);
    }

    function updateDropdowns(code) {
        const lang = LANGUAGES.find(l => l.code === code) || LANGUAGES[0];
        document.querySelectorAll('.dfs-lang-btn').forEach(btn => {
            btn.innerHTML = `${lang.flag} <span class="dfs-lang-name">${lang.name}</span> <i class="fas fa-chevron-down" style="font-size:.65rem;opacity:.7;margin-left:3px;"></i>`;
        });
        document.querySelectorAll('.dfs-lang-item').forEach(item => {
            const chk = item.querySelector('.dfs-chk');
            if (chk) chk.style.display = item.dataset.code === code ? 'inline' : 'none';
        });
    }

    function buildDropdown(curCode) {
        const cur = LANGUAGES.find(l => l.code === curCode) || LANGUAGES[0];
        return `<div class="dfs-lang-wrapper" style="position:relative;display:inline-flex;align-items:center;">
  <button class="dfs-lang-btn" onclick="window.DFSi18n.toggle(event)"
    style="display:inline-flex;align-items:center;gap:5px;background:transparent;
           border:1px solid rgba(102,126,234,0.3);border-radius:8px;padding:5px 11px;
           cursor:pointer;color:inherit;font-size:.82rem;font-family:inherit;transition:all .2s;white-space:nowrap;"
    onmouseover="this.style.borderColor='rgba(102,126,234,.7)';this.style.background='rgba(102,126,234,.08)'"
    onmouseout="this.style.borderColor='rgba(102,126,234,.3)';this.style.background='transparent'">
    ${cur.flag} <span class="dfs-lang-name">${cur.name}</span>
    <i class="fas fa-chevron-down" style="font-size:.65rem;opacity:.7;margin-left:3px;"></i>
  </button>
  <div class="dfs-lang-menu" style="display:none;position:absolute;top:calc(100% + 7px);right:0;
       background:var(--bg-secondary,#0f1123);border:1px solid rgba(102,126,234,.25);
       border-radius:12px;padding:5px;min-width:152px;z-index:99999;
       box-shadow:0 16px 48px rgba(0,0,0,.5);max-height:290px;overflow-y:auto;">
    ${LANGUAGES.map(l => `<div class="dfs-lang-item" data-code="${l.code}"
      onclick="window.DFSi18n.select('${l.code}')"
      style="display:flex;align-items:center;gap:8px;padding:7px 10px;border-radius:7px;
             cursor:pointer;font-size:.82rem;color:inherit;transition:background .15s;"
      onmouseover="this.style.background='rgba(102,126,234,.14)'"
      onmouseout="this.style.background='transparent'">
      <span style="font-size:1rem;">${l.flag}</span>
      <span style="flex:1;">${l.name}</span>
      <i class="fas fa-check dfs-chk" style="font-size:.7rem;color:#667eea;display:${l.code===curCode?'inline':'none'};"></i>
    </div>`).join('')}
  </div>
</div>`;
    }

    function replaceSelectors() {
        const cur = localStorage.getItem('dfs_lang') || 'en';
        // Replace .dfs-translate-bar contents
        document.querySelectorAll('.dfs-translate-bar').forEach(bar => {
            bar.innerHTML = buildDropdown(cur);
        });
        // Replace standalone select.dfs-lang-select
        document.querySelectorAll('select.dfs-lang-select').forEach(sel => {
            const tmp = document.createElement('span');
            tmp.innerHTML = buildDropdown(cur);
            sel.parentNode.replaceChild(tmp.firstElementChild, sel);
        });
        // If none found, inject before user-menu in navbar
        if (!document.querySelector('.dfs-lang-wrapper')) {
            const targets = ['.navbar-end','.nav-right','nav .ms-auto','.navbar-nav.ms-auto','.d-flex.align-items-center'];
            for (const t of targets) {
                const el = document.querySelector(t);
                if (el) {
                    const wrap = document.createElement('div');
                    wrap.style.cssText = 'display:inline-flex;align-items:center;margin:0 6px;';
                    wrap.innerHTML = buildDropdown(cur);
                    el.insertBefore(wrap, el.firstChild);
                    break;
                }
            }
        }
    }

    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dfs-lang-wrapper'))
            document.querySelectorAll('.dfs-lang-menu').forEach(m => m.style.display='none');
    });

    function applySaved() {
        const s = localStorage.getItem('dfs_lang');
        if (s && s !== 'en') {
            const val = `/en/${s}`;
            if (!document.cookie.includes(`googtrans=${val}`)) {
                document.cookie = `googtrans=${val}; path=/`;
                document.cookie = `googtrans=${val}; path=/; domain=.${location.hostname}`;
            }
        }
    }

    window.DFSi18n = {
        toggle: function(e) {
            e.stopPropagation();
            const menu = e.currentTarget.parentElement.querySelector('.dfs-lang-menu');
            if (!menu) return;
            const open = menu.style.display === 'block';
            document.querySelectorAll('.dfs-lang-menu').forEach(m => m.style.display='none');
            menu.style.display = open ? 'none' : 'block';
        },
        select: function(code) {
            document.querySelectorAll('.dfs-lang-menu').forEach(m => m.style.display='none');
            applyLanguage(code);
        }
    };

    applySaved();
    injectHideStyles();

    const init = function() {
        injectGTContainer();
        loadGT();
        replaceSelectors();
    };

    document.readyState === 'loading'
        ? document.addEventListener('DOMContentLoaded', init)
        : setTimeout(init, 50);

    window.addEventListener('load', function() {
        setTimeout(function() {
            injectHideStyles();
            replaceSelectors();
            const s = localStorage.getItem('dfs_lang');
            if (s && s !== 'en') updateDropdowns(s);
        }, 900);
    });

})();