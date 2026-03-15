/* ═══════════════════════════════════════════════════════════════
   DeepFake Shield — Main JavaScript
   Core functionality: Navigation, Dropdowns, File Upload,
   Scroll Effects, Cookie Banner, Utilities
   ═══════════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    /* ─────────────────────────────────────────────
       DOM Ready
       ───────────────────────────────────────────── */
    document.addEventListener('DOMContentLoaded', function () {
        initNavbar();
        initMobileMenu();
        initDropdowns();
        initScrollToTop();
        initCookieBanner();
        initFileUpload();
        initFormSubmitLoading();
        initSmoothScrollLinks();
        initCountUpNumbers();
    });

    /* ─────────────────────────────────────────────
       Navbar Scroll Effect
       ───────────────────────────────────────────── */
    function initNavbar() {
        var navbar = document.getElementById('navbar');
        if (!navbar) return;

        var lastScroll = 0;
        var scrollThreshold = 50;

        function handleScroll() {
            var currentScroll = window.pageYOffset || document.documentElement.scrollTop;

            if (currentScroll > scrollThreshold) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }

            lastScroll = currentScroll;
        }

        var scrollTicking = false;
        window.addEventListener('scroll', function () {
            if (!scrollTicking) {
                window.requestAnimationFrame(function () {
                    handleScroll();
                    scrollTicking = false;
                });
                scrollTicking = true;
            }
        }, { passive: true });

        handleScroll();
    }

    /* ─────────────────────────────────────────────
       Mobile Menu
       ───────────────────────────────────────────── */
    function initMobileMenu() {
        var toggle = document.getElementById('mobile-menu-toggle');
        var menu = document.getElementById('mobile-menu');
        if (!toggle || !menu) return;

        toggle.addEventListener('click', function (e) {
            e.stopPropagation();
            var isOpen = menu.classList.contains('open');

            if (isOpen) {
                closeMobileMenu(toggle, menu);
            } else {
                openMobileMenu(toggle, menu);
            }
        });

        // Close on link click
        var links = menu.querySelectorAll('.mobile-nav-link');
        links.forEach(function (link) {
            link.addEventListener('click', function () {
                closeMobileMenu(toggle, menu);
            });
        });

        // Close on outside click
        document.addEventListener('click', function (e) {
            if (menu.classList.contains('open') && !menu.contains(e.target) && !toggle.contains(e.target)) {
                closeMobileMenu(toggle, menu);
            }
        });

        // Close on escape
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && menu.classList.contains('open')) {
                closeMobileMenu(toggle, menu);
            }
        });

        // Close on resize
        window.addEventListener('resize', function () {
            if (window.innerWidth > 768 && menu.classList.contains('open')) {
                closeMobileMenu(toggle, menu);
            }
        });
    }

    function openMobileMenu(toggle, menu) {
        toggle.classList.add('active');
        menu.classList.add('open');
        menu.style.display = 'block';
        // Force reflow for animation
        menu.offsetHeight;
        menu.style.opacity = '1';
        menu.style.transform = 'translateY(0)';
        menu.style.pointerEvents = 'auto';
        document.body.style.overflow = 'hidden';
    }

    function closeMobileMenu(toggle, menu) {
        toggle.classList.remove('active');
        menu.style.opacity = '0';
        menu.style.transform = 'translateY(-10px)';
        menu.style.pointerEvents = 'none';
        document.body.style.overflow = '';
        setTimeout(function () {
            menu.classList.remove('open');
        }, 250);
    }

    /* ─────────────────────────────────────────────
       Dropdown Menus
       ───────────────────────────────────────────── */
    function initDropdowns() {
        var dropdowns = document.querySelectorAll('.nav-dropdown');

        dropdowns.forEach(function (dropdown) {
            var trigger = dropdown.querySelector('.dropdown-trigger');
            if (!trigger) return;

            // Desktop: hover
            if (window.matchMedia('(hover: hover)').matches) {
                dropdown.addEventListener('mouseenter', function () {
                    closeAllDropdowns(dropdowns);
                    dropdown.classList.add('open');
                });
                dropdown.addEventListener('mouseleave', function () {
                    dropdown.classList.remove('open');
                });
            }

            // Touch/click fallback
            trigger.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                var isOpen = dropdown.classList.contains('open');
                closeAllDropdowns(dropdowns);
                if (!isOpen) {
                    dropdown.classList.add('open');
                }
            });
        });

        // Close dropdowns on outside click
        document.addEventListener('click', function (e) {
            var isInside = false;
            dropdowns.forEach(function (d) {
                if (d.contains(e.target)) isInside = true;
            });
            if (!isInside) {
                closeAllDropdowns(dropdowns);
            }
        });

        // Close on escape
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                closeAllDropdowns(dropdowns);
            }
        });
    }

    function closeAllDropdowns(dropdowns) {
        dropdowns.forEach(function (d) {
            d.classList.remove('open');
        });
    }

    /* ─────────────────────────────────────────────
       Scroll to Top Button
       ───────────────────────────────────────────── */
    function initScrollToTop() {
        var btn = document.getElementById('scroll-top-btn');
        if (!btn) return;

        var ticking = false;
        window.addEventListener('scroll', function () {
            if (!ticking) {
                window.requestAnimationFrame(function () {
                    if (window.pageYOffset > 400) {
                        btn.classList.add('visible');
                    } else {
                        btn.classList.remove('visible');
                    }
                    ticking = false;
                });
                ticking = true;
            }
        }, { passive: true });

        btn.addEventListener('click', function () {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    /* ─────────────────────────────────────────────
       Cookie Banner
       ───────────────────────────────────────────── */
    function initCookieBanner() {
        var banner = document.getElementById('cookie-banner');
        var acceptBtn = document.getElementById('cookie-accept');
        if (!banner || !acceptBtn) return;

        // Check if already accepted
        var cookieAccepted = localStorage.getItem('dfs_cookie_accepted');
        if (!cookieAccepted) {
            setTimeout(function () {
                banner.style.display = 'block';
            }, 2000);
        }

        acceptBtn.addEventListener('click', function () {
            localStorage.setItem('dfs_cookie_accepted', 'true');
            banner.style.opacity = '0';
            banner.style.transform = 'translateY(20px)';
            banner.style.transition = 'opacity 0.4s, transform 0.4s';
            setTimeout(function () {
                banner.style.display = 'none';
            }, 400);
        });
    }

    /* ─────────────────────────────────────────────
       File Upload (Drag & Drop + Preview)
       ───────────────────────────────────────────── */
    function initFileUpload() {
        var dropZone = document.getElementById('drop-zone');
        var fileInput = document.getElementById('file-input');
        var preview = document.getElementById('file-preview');
        var previewImg = document.getElementById('preview-img');
        var previewName = document.getElementById('preview-name');
        var previewSize = document.getElementById('preview-size');
        var removeBtn = document.getElementById('remove-file');
        var submitBtn = document.getElementById('submit-btn');

        if (!dropZone || !fileInput) return;

        // Prevent defaults for drag events
        var preventDefaults = function (e) {
            e.preventDefault();
            e.stopPropagation();
        };

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(function (evt) {
            dropZone.addEventListener(evt, preventDefaults, false);
            document.body.addEventListener(evt, preventDefaults, false);
        });

        // Highlight drop zone
        ['dragenter', 'dragover'].forEach(function (evt) {
            dropZone.addEventListener(evt, function () {
                dropZone.classList.add('drag-over');
            });
        });

        ['dragleave', 'drop'].forEach(function (evt) {
            dropZone.addEventListener(evt, function () {
                dropZone.classList.remove('drag-over');
            });
        });

        // Handle dropped files
        dropZone.addEventListener('drop', function (e) {
            var files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect(files[0]);
            }
        });

        // Handle file input change
        fileInput.addEventListener('change', function () {
            if (this.files.length > 0) {
                handleFileSelect(this.files[0]);
            }
        });

        // Remove file
        if (removeBtn) {
            removeBtn.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                clearFileSelection();
            });
        }

        function handleFileSelect(file) {
            if (!file) return;

            // Show preview
            if (preview) {
                preview.style.display = 'flex';
                preview.style.animation = 'fadeInUp 0.4s ease-out';
            }

            // Set name and size
            if (previewName) previewName.textContent = file.name;
            if (previewSize) previewSize.textContent = formatFileSize(file.size);

            // Image preview
            if (previewImg && file.type.startsWith('image/')) {
                var reader = new FileReader();
                reader.onload = function (e) {
                    previewImg.src = e.target.result;
                    var wrap = previewImg.closest('.preview-image-wrap');
                    if (wrap) wrap.style.display = 'block';
                };
                reader.readAsDataURL(file);
            } else if (previewImg) {
                var wrap = previewImg.closest('.preview-image-wrap');
                if (wrap) wrap.style.display = 'none';
            }

            // Hide drop zone content
            var dzContent = dropZone.querySelector('.drop-zone-content');
            if (dzContent) dzContent.style.display = 'none';
            dropZone.style.borderStyle = 'solid';
            dropZone.style.borderColor = 'var(--color-success)';
            dropZone.style.padding = '1rem';

            // Enable submit
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.style.animation = 'pulseGlow 2s ease infinite';
            }
        }

        function clearFileSelection() {
            fileInput.value = '';
            if (preview) {
                preview.style.display = 'none';
            }
            var dzContent = dropZone.querySelector('.drop-zone-content');
            if (dzContent) dzContent.style.display = 'block';
            dropZone.style.borderStyle = 'dashed';
            dropZone.style.borderColor = '';
            dropZone.style.padding = '';

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.style.animation = '';
            }

            if (previewImg) previewImg.src = '';
        }
    }

    /* ─────────────────────────────────────────────
       Form Submit Loading State
       ───────────────────────────────────────────── */
    function initFormSubmitLoading() {
        var form = document.getElementById('upload-form');
        var loading = document.getElementById('analysis-loading');
        var submitBtn = document.getElementById('submit-btn');

        if (!form || !loading) return;

        form.addEventListener('submit', function (e) {
            // Check if file is selected
            var fileInput = document.getElementById('file-input');
            if (fileInput && fileInput.files.length === 0) {
                e.preventDefault();
                showNotification('Please select a file first.', 'warning');
                return;
            }

            // Show loading
            var uploadCard = form.closest('.upload-card');
            if (uploadCard) {
                form.style.display = 'none';
                loading.style.display = 'flex';
                loading.style.animation = 'fadeInUp 0.5s ease-out';

                // Animate loading steps
                var steps = loading.querySelectorAll('.loading-step');
                steps.forEach(function (step, index) {
                    setTimeout(function () {
                        step.classList.add('active');
                        var icon = step.querySelector('i');
                        if (icon) {
                            icon.className = 'fas fa-check-circle';
                        }
                    }, (index + 1) * 1200);
                });
            }

            // Disable submit button
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Analyzing...</span>';
            }
        });
    }

    /* ─────────────────────────────────────────────
       Smooth Scroll for Anchor Links
       ───────────────────────────────────────────── */
    function initSmoothScrollLinks() {
        var links = document.querySelectorAll('a[href^="#"]');
        links.forEach(function (link) {
            link.addEventListener('click', function (e) {
                var targetId = this.getAttribute('href');
                if (targetId === '#' || targetId.length < 2) return;

                var target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    var navbarHeight = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--navbar-height')) || 70;
                    var offsetTop = target.getBoundingClientRect().top + window.pageYOffset - navbarHeight - 20;

                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    /* ─────────────────────────────────────────────
       Animated Count-Up Numbers
       ───────────────────────────────────────────── */
    function initCountUpNumbers() {
        var numbers = document.querySelectorAll('[data-count]');
        if (numbers.length === 0) return;

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    var el = entry.target;
                    var target = parseInt(el.getAttribute('data-count'), 10);
                    if (isNaN(target)) return;

                    animateNumber(el, 0, target, 1500);
                    observer.unobserve(el);
                }
            });
        }, {
            threshold: 0.3,
            rootMargin: '0px'
        });

        numbers.forEach(function (num) {
            observer.observe(num);
        });
    }

    function animateNumber(el, start, end, duration) {
        var startTime = null;
        var range = end - start;

        function step(timestamp) {
            if (!startTime) startTime = timestamp;
            var progress = Math.min((timestamp - startTime) / duration, 1);

            // Ease out cubic
            var eased = 1 - Math.pow(1 - progress, 3);
            var current = Math.floor(start + range * eased);

            el.textContent = current.toLocaleString();

            if (progress < 1) {
                requestAnimationFrame(step);
            } else {
                el.textContent = end.toLocaleString();
            }
        }

        requestAnimationFrame(step);
    }

    /* ─────────────────────────────────────────────
       Utility: Format File Size
       ───────────────────────────────────────────── */
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        var k = 1024;
        var sizes = ['Bytes', 'KB', 'MB', 'GB'];
        var i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    /* ─────────────────────────────────────────────
       Utility: Show Notification
       ───────────────────────────────────────────── */
    window.showNotification = function (message, type) {
        type = type || 'info';
        var container = document.getElementById('alerts-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'alerts-container';
            container.id = 'alerts-container';
            document.body.appendChild(container);
        }

        var iconMap = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };

        var alert = document.createElement('div');
        alert.className = 'alert alert-' + type;
        alert.innerHTML =
            '<div class="alert-icon"><i class="fas ' + (iconMap[type] || iconMap.info) + '"></i></div>' +
            '<div class="alert-content"><span class="alert-text">' + message + '</span></div>' +
            '<button class="alert-close" onclick="this.parentElement.remove()"><i class="fas fa-times"></i></button>';

        container.appendChild(alert);

        // Auto dismiss
        setTimeout(function () {
            if (alert.parentElement) {
                alert.style.opacity = '0';
                alert.style.transform = 'translateX(40px)';
                setTimeout(function () {
                    if (alert.parentElement) alert.remove();
                }, 400);
            }
        }, 5000);
    };

    /* ─────────────────────────────────────────────
       Utility: Debounce
       ───────────────────────────────────────────── */
    window.debounce = function (func, wait) {
        var timeout;
        return function () {
            var context = this;
            var args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(function () {
                func.apply(context, args);
            }, wait);
        };
    };

    /* ─────────────────────────────────────────────
       Utility: Throttle
       ───────────────────────────────────────────── */
    window.throttle = function (func, limit) {
        var inThrottle;
        return function () {
            var context = this;
            var args = arguments;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(function () {
                    inThrottle = false;
                }, limit);
            }
        };
    };

})();