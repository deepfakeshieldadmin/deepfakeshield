/* ═══════════════════════════════════════════════════════════════
   DeepFake Shield — Landing Page JavaScript
   Matrix Background | Logo Intro Animation | Typing Effect
   Particle Field | Stats Counter | Scroll Transition
   ═══════════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        initMatrixBackground();
        initParticleField();
        initLogoIntro();
        initLandingStats();
        initLanguageSelector();
    });

    /* ═══════════════════════════════════════════════
       Matrix Rain Background
       ═══════════════════════════════════════════════ */
    function initMatrixBackground() {
        var canvas = document.getElementById('matrix-canvas');
        if (!canvas) return;

        var ctx = canvas.getContext('2d');
        if (!ctx) return;

        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }

        resize();
        window.addEventListener('resize', debounce(resize, 200));

        // Characters
        var chars = 'DEEPFAKESHIELD01アイウエオカキクケコサシスセソ♦♢◊∞≈≠∑∏πΩ';
        var charArray = chars.split('');
        var fontSize = 14;
        var columns = Math.floor(canvas.width / fontSize);
        var drops = [];

        for (var i = 0; i < columns; i++) {
            drops[i] = Math.random() * -100;
        }

        var hue = 250; // Purple-blue hue

        function drawMatrix() {
            // Semi-transparent black to create fade effect
            ctx.fillStyle = 'rgba(10, 14, 26, 0.06)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.font = fontSize + 'px "JetBrains Mono", monospace';

            for (var i = 0; i < drops.length; i++) {
                var charIndex = Math.floor(Math.random() * charArray.length);
                var char = charArray[charIndex];

                // Vary colors between cyan-blue-purple
                var localHue = hue + Math.sin(i * 0.1 + Date.now() * 0.001) * 30;
                var brightness = 40 + Math.random() * 30;
                ctx.fillStyle = 'hsla(' + localHue + ', 80%, ' + brightness + '%, 0.8)';

                var x = i * fontSize;
                var y = drops[i] * fontSize;

                ctx.fillText(char, x, y);

                // Reset drop randomly
                if (y > canvas.height && Math.random() > 0.985) {
                    drops[i] = 0;
                }

                drops[i]++;
            }

            hue += 0.02;
            if (hue > 360) hue = 0;
        }

        // Run at lower FPS for performance
        var matrixInterval = setInterval(drawMatrix, 50);

        // Cleanup when leaving page
        window.addEventListener('beforeunload', function () {
            clearInterval(matrixInterval);
        });

        // Reduce animation if page is hidden
        document.addEventListener('visibilitychange', function () {
            if (document.hidden) {
                clearInterval(matrixInterval);
            } else {
                matrixInterval = setInterval(drawMatrix, 50);
            }
        });
    }

    /* ═══════════════════════════════════════════════
       Particle Field
       ═══════════════════════════════════════════════ */
    function initParticleField() {
        var field = document.getElementById('particle-field');
        if (!field) return;

        var particleCount = Math.min(30, Math.floor(window.innerWidth / 50));

        for (var i = 0; i < particleCount; i++) {
            createParticle(field);
        }
    }

    function createParticle(container) {
        var particle = document.createElement('div');
        var size = Math.random() * 4 + 1;
        var x = Math.random() * 100;
        var y = Math.random() * 100;
        var duration = Math.random() * 15 + 10;
        var delay = Math.random() * 10;
        var driftX = (Math.random() - 0.5) * 100;
        var driftY = (Math.random() - 0.5) * 100;

        particle.style.cssText =
            'position:absolute;' +
            'width:' + size + 'px;' +
            'height:' + size + 'px;' +
            'background:rgba(102,126,234,' + (Math.random() * 0.3 + 0.1) + ');' +
            'border-radius:50%;' +
            'left:' + x + '%;' +
            'top:' + y + '%;' +
            'pointer-events:none;' +
            '--drift-x:' + driftX + 'px;' +
            '--drift-y:' + driftY + 'px;' +
            'animation:particleDrift ' + duration + 's ' + delay + 's ease-in-out infinite;';

        container.appendChild(particle);
    }

    /* ═══════════════════════════════════════════════
       Logo Intro Animation
       ═══════════════════════════════════════════════ */
    function initLogoIntro() {
        var intro = document.getElementById('logo-intro');
        var hero = document.getElementById('landing-hero');
        var features = document.getElementById('landing-features');
        var typingText = document.getElementById('typing-text');

        if (!intro || !hero) return;

        // Typing animation for tagline
        var tagline = 'Real-Time Media Authenticity Verification System';
        var charIndex = 0;
        var typingSpeed = 40;
        var typingStartDelay = 1200;

        function typeCharacter() {
            if (!typingText) return;
            if (charIndex < tagline.length) {
                typingText.textContent += tagline.charAt(charIndex);
                charIndex++;
                setTimeout(typeCharacter, typingSpeed);
            }
        }

        setTimeout(typeCharacter, typingStartDelay);

        // Transition from intro to hero
        var introDuration = 4000; // Total intro display time

        setTimeout(function () {
            // Fade out intro
            intro.classList.add('fade-out');

            setTimeout(function () {
                intro.style.display = 'none';

                // Show hero
                hero.style.display = 'flex';
                hero.style.opacity = '0';
                hero.style.animation = 'fadeInUp 1s ease-out forwards';

                // Show features
                if (features) {
                    features.style.display = 'block';
                }

                // Reinitialize AOS for newly visible elements
                setTimeout(function () {
                    if (typeof AOS !== 'undefined') {
                        AOS.refresh();
                    }
                }, 200);

                // Start stat counters
                setTimeout(function () {
                    animateLandingStats();
                }, 800);

            }, 800); // Wait for fade-out animation

        }, introDuration);
    }

    /* ═══════════════════════════════════════════════
       Landing Page Stats Counter
       ═══════════════════════════════════════════════ */
    function initLandingStats() {
        // Stats will be animated after intro completes
    }

    function animateLandingStats() {
        var statNumbers = document.querySelectorAll('.hero-stats .stat-number');
        statNumbers.forEach(function (el) {
            var target = parseInt(el.getAttribute('data-count'), 10);
            if (isNaN(target)) return;
            animateCount(el, 0, target, 1800);
        });
    }

    function animateCount(el, start, end, duration) {
        var startTime = null;
        var range = end - start;

        function step(timestamp) {
            if (!startTime) startTime = timestamp;
            var progress = Math.min((timestamp - startTime) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            var current = Math.floor(start + range * eased);

            el.textContent = current;

            if (progress < 1) {
                requestAnimationFrame(step);
            } else {
                el.textContent = end;
            }
        }

        requestAnimationFrame(step);
    }

    /* ═══════════════════════════════════════════════
       Language Selector
       ═══════════════════════════════════════════════ */
    function initLanguageSelector() {
        var langBtns = document.querySelectorAll('.lang-btn');
        if (langBtns.length === 0) return;

        langBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                // Remove active from all
                langBtns.forEach(function (b) {
                    b.classList.remove('active');
                });
                // Set active
                btn.classList.add('active');

                var lang = btn.getAttribute('data-lang');
                localStorage.setItem('dfs_language', lang);

                // Optional: Update text content based on language
                // This is a simplified version; full i18n would use a translation system
                updateLanguageDisplay(lang);
            });
        });

        // Load saved language
        var savedLang = localStorage.getItem('dfs_language') || 'en';
        langBtns.forEach(function (btn) {
            btn.classList.remove('active');
            if (btn.getAttribute('data-lang') === savedLang) {
                btn.classList.add('active');
            }
        });
    }

    function updateLanguageDisplay(lang) {
        // Simplified language switching for demo purposes
        var translations = {
            en: {
                heroLine1: 'Defend Against',
                heroLine2: 'Digital Deception',
                enterBtn: 'Enter Shield',
                createBtn: 'Create Account'
            },
            hi: {
                heroLine1: 'डिजिटल धोखाधड़ी से',
                heroLine2: 'सुरक्षा करें',
                enterBtn: 'शील्ड में प्रवेश',
                createBtn: 'खाता बनाएं'
            },
            es: {
                heroLine1: 'Defiéndete Contra',
                heroLine2: 'El Engaño Digital',
                enterBtn: 'Entrar al Escudo',
                createBtn: 'Crear Cuenta'
            },
            fr: {
                heroLine1: 'Défendez-vous Contre',
                heroLine2: 'La Tromperie Numérique',
                enterBtn: 'Entrer dans le Bouclier',
                createBtn: 'Créer un Compte'
            },
            de: {
                heroLine1: 'Verteidigen Sie Sich Gegen',
                heroLine2: 'Digitale Täuschung',
                enterBtn: 'Schild betreten',
                createBtn: 'Konto Erstellen'
            }
        };

        var t = translations[lang] || translations.en;

        var line1 = document.querySelector('.hero-title-line');
        var line2 = document.querySelector('.hero-title-gradient');

        if (line1) line1.textContent = t.heroLine1;
        if (line2) line2.textContent = t.heroLine2;

        // Update buttons
        var btns = document.querySelectorAll('.hero-actions .btn-content span');
        if (btns.length >= 2) {
            btns[0].textContent = t.enterBtn;
            btns[1].textContent = t.createBtn;
        }
    }

    /* ═══════════════════════════════════════════════
       Utility: Debounce
       ═══════════════════════════════════════════════ */
    function debounce(func, wait) {
        var timeout;
        return function () {
            var context = this;
            var args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(function () {
                func.apply(context, args);
            }, wait);
        };
    }

})();