/* ═══════════════════════════════════════════════════════════════
   DeepFake Shield — Custom Animations & Scroll Effects
   Extends AOS with IntersectionObserver-based triggers,
   parallax, counter animations, and reveal effects
   ═══════════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        initScrollReveal();
        initParallaxElements();
        initProgressBars();
        initScoreCircles();
        initStaggeredCards();
        initHoverEffects();
        initTypingEffect();
    });

    /* ─────────────────────────────────────────────
       Scroll Reveal (IntersectionObserver)
       Additional reveal effects beyond AOS
       ───────────────────────────────────────────── */
    function initScrollReveal() {
        var revealElements = document.querySelectorAll('.reveal-on-scroll');
        if (revealElements.length === 0) return;

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.15,
            rootMargin: '0px 0px -50px 0px'
        });

        revealElements.forEach(function (el) {
            observer.observe(el);
        });
    }

    /* ─────────────────────────────────────────────
       Parallax Scroll Effect
       ───────────────────────────────────────────── */
    function initParallaxElements() {
        var parallaxItems = document.querySelectorAll('.parallax-item');
        if (parallaxItems.length === 0) return;

        var ticking = false;

        function updateParallax() {
            var scrollY = window.pageYOffset;

            parallaxItems.forEach(function (item) {
                var speed = parseFloat(item.getAttribute('data-parallax-speed')) || 0.3;
                var rect = item.getBoundingClientRect();
                var windowHeight = window.innerHeight;

                if (rect.top < windowHeight && rect.bottom > 0) {
                    var yOffset = (scrollY - item.offsetTop) * speed;
                    item.style.transform = 'translateY(' + yOffset + 'px)';
                }
            });
        }

        window.addEventListener('scroll', function () {
            if (!ticking) {
                requestAnimationFrame(function () {
                    updateParallax();
                    ticking = false;
                });
                ticking = true;
            }
        }, { passive: true });
    }

    /* ─────────────────────────────────────────────
       Progress Bars Animation
       ───────────────────────────────────────────── */
    function initProgressBars() {
        var bars = document.querySelectorAll('.frame-score-fill, .score-bar-fill');
        if (bars.length === 0) return;

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    var bar = entry.target;
                    var targetWidth = bar.style.width;

                    // Reset and animate
                    bar.style.width = '0';
                    bar.style.transition = 'none';

                    requestAnimationFrame(function () {
                        requestAnimationFrame(function () {
                            bar.style.transition = 'width 1.5s cubic-bezier(0.4, 0, 0.2, 1)';
                            bar.style.width = targetWidth;
                        });
                    });

                    observer.unobserve(bar);
                }
            });
        }, {
            threshold: 0.2
        });

        bars.forEach(function (bar) {
            observer.observe(bar);
        });
    }

    /* ─────────────────────────────────────────────
       Score Circle SVG Animation
       ───────────────────────────────────────────── */
    function initScoreCircles() {
        var circles = document.querySelectorAll('.score-circle');
        if (circles.length === 0) return;

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    var circleWrap = entry.target;
                    var score = parseFloat(circleWrap.getAttribute('data-score')) || 0;
                    var fillCircle = circleWrap.querySelector('.score-ring-fill');

                    if (fillCircle) {
                        var circumference = 339.292; // 2 * PI * 54
                        var offset = circumference - (circumference * score) / 100;

                        // Reset
                        fillCircle.style.transition = 'none';
                        fillCircle.style.strokeDashoffset = circumference;

                        requestAnimationFrame(function () {
                            requestAnimationFrame(function () {
                                fillCircle.style.transition = 'stroke-dashoffset 2s cubic-bezier(0.4, 0, 0.2, 1)';
                                fillCircle.style.strokeDashoffset = offset;
                            });
                        });
                    }

                    // Animate number
                    var scoreNumber = circleWrap.querySelector('.score-number');
                    if (scoreNumber) {
                        animateNumberTo(scoreNumber, score, 2000);
                    }

                    observer.unobserve(circleWrap);
                }
            });
        }, {
            threshold: 0.3
        });

        circles.forEach(function (circle) {
            observer.observe(circle);
        });
    }

    function animateNumberTo(el, target, duration) {
        var startTime = null;
        var startVal = 0;
        var hasDecimal = target % 1 !== 0;

        function step(timestamp) {
            if (!startTime) startTime = timestamp;
            var progress = Math.min((timestamp - startTime) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 4); // Ease out quart
            var current = startVal + (target - startVal) * eased;

            if (hasDecimal) {
                el.textContent = current.toFixed(1);
            } else {
                el.textContent = Math.floor(current);
            }

            if (progress < 1) {
                requestAnimationFrame(step);
            } else {
                el.textContent = hasDecimal ? target.toFixed(1) : target;
            }
        }

        requestAnimationFrame(step);
    }

    /* ─────────────────────────────────────────────
       Staggered Card Animations
       ───────────────────────────────────────────── */
    function initStaggeredCards() {
        var staggerContainers = document.querySelectorAll('.stagger-children');
        if (staggerContainers.length === 0) return;

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    var children = entry.target.children;
                    Array.prototype.forEach.call(children, function (child, index) {
                        setTimeout(function () {
                            child.style.opacity = '1';
                            child.style.transform = 'translateY(0)';
                        }, index * 80);
                    });
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1
        });

        staggerContainers.forEach(function (container) {
            // Set initial state
            Array.prototype.forEach.call(container.children, function (child) {
                child.style.opacity = '0';
                child.style.transform = 'translateY(20px)';
                child.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            });
            observer.observe(container);
        });
    }

    /* ─────────────────────────────────────────────
       Hover Effects Enhancement
       ───────────────────────────────────────────── */
    function initHoverEffects() {
        // Tilt effect for cards on desktop
        if (window.matchMedia('(hover: hover) and (min-width: 769px)').matches) {
            var tiltCards = document.querySelectorAll(
                '.detection-card, .feature-card, .quick-action-card, .stat-card'
            );

            tiltCards.forEach(function (card) {
                card.addEventListener('mousemove', function (e) {
                    var rect = card.getBoundingClientRect();
                    var x = e.clientX - rect.left;
                    var y = e.clientY - rect.top;
                    var centerX = rect.width / 2;
                    var centerY = rect.height / 2;
                    var rotateX = ((y - centerY) / centerY) * -4;
                    var rotateY = ((x - centerX) / centerX) * 4;

                    card.style.transform =
                        'perspective(1000px) rotateX(' + rotateX + 'deg) rotateY(' + rotateY + 'deg) translateY(-6px)';
                });

                card.addEventListener('mouseleave', function () {
                    card.style.transform = '';
                    card.style.transition = 'transform 0.5s ease';
                    setTimeout(function () {
                        card.style.transition = '';
                    }, 500);
                });
            });
        }

        // Magnetic button effect
        if (window.matchMedia('(hover: hover)').matches) {
            var magneticBtns = document.querySelectorAll('.btn-hero-primary, .btn-hero-secondary');
            magneticBtns.forEach(function (btn) {
                btn.addEventListener('mousemove', function (e) {
                    var rect = btn.getBoundingClientRect();
                    var x = e.clientX - rect.left - rect.width / 2;
                    var y = e.clientY - rect.top - rect.height / 2;
                    btn.style.transform = 'translate(' + (x * 0.15) + 'px, ' + (y * 0.15 - 3) + 'px)';
                });
                btn.addEventListener('mouseleave', function () {
                    btn.style.transform = '';
                });
            });
        }
    }

    /* ─────────────────────────────────────────────
       Typing Effect (for any element with data-typing)
       ───────────────────────────────────────────── */
    function initTypingEffect() {
        var typingElements = document.querySelectorAll('[data-typing]');
        typingElements.forEach(function (el) {
            var text = el.getAttribute('data-typing');
            var speed = parseInt(el.getAttribute('data-typing-speed'), 10) || 50;
            typeText(el, text, speed);
        });
    }

    function typeText(element, text, speed) {
        var index = 0;
        element.textContent = '';

        function type() {
            if (index < text.length) {
                element.textContent += text.charAt(index);
                index++;
                setTimeout(type, speed);
            }
        }

        // Start after a small delay
        setTimeout(type, 500);
    }

    /* ─────────────────────────────────────────────
       Expose utilities globally
       ───────────────────────────────────────────── */
    window.DFSAnimations = {
        animateNumber: animateNumberTo,
        typeText: typeText
    };

})();