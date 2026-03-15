/* ============================================
   DEEPFAKE SHIELD — MAIN JS (FIXED)
   ============================================ */

document.addEventListener("DOMContentLoaded", () => {

    // === PAGE LOADER — FIXED: Never gets stuck ===
    const loader = document.getElementById("pageLoader");
    if (loader) {
        // Quick show then hide
        setTimeout(() => {
            loader.classList.add("hidden");
        }, 1000);
        
        // Absolute fallback — force remove
        setTimeout(() => {
            if (loader) {
                loader.style.opacity = "0";
                loader.style.pointerEvents = "none";
                loader.style.visibility = "hidden";
                loader.style.display = "none";
            }
        }, 2000);
    }

    // === COOKIE BANNER ===
    const cookieBanner = document.getElementById("cookieBanner");
    const acceptBtn = document.getElementById("acceptCookiesBtn");
    if (cookieBanner && !localStorage.getItem("cookieAccepted")) {
        setTimeout(() => {
            cookieBanner.classList.add("show");
        }, 2500);
    }
    if (acceptBtn) {
        acceptBtn.addEventListener("click", () => {
            localStorage.setItem("cookieAccepted", "true");
            cookieBanner.classList.remove("show");
        });
    }

    // === PASSWORD TOGGLE (Single Eye Only) ===
    document.querySelectorAll(".password-toggle-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const targetId = btn.getAttribute("data-target");
            const input = document.getElementById(targetId);
            const icon = btn.querySelector("i");
            if (!input) return;
            if (input.type === "password") {
                input.type = "text";
                icon.className = "bi bi-eye-slash-fill";
            } else {
                input.type = "password";
                icon.className = "bi bi-eye-fill";
            }
        });
    });

    // === NAVBAR SCROLL EFFECT ===
    const navbar = document.getElementById("mainNav");
    if (navbar) {
        const handleScroll = () => {
            if (window.scrollY > 60) {
                navbar.classList.add("scrolled");
            } else {
                navbar.classList.remove("scrolled");
            }
        };
        window.addEventListener("scroll", handleScroll, { passive: true });
        handleScroll();
    }

    // === BACK TO TOP ===
    const backToTopBtn = document.getElementById("backToTopBtn");
    if (backToTopBtn) {
        window.addEventListener("scroll", () => {
            if (window.scrollY > 400) {
                backToTopBtn.classList.add("visible");
            } else {
                backToTopBtn.classList.remove("visible");
            }
        }, { passive: true });
        backToTopBtn.addEventListener("click", () => {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }

    // === COUNTER ANIMATION ===
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const target = parseInt(el.getAttribute("data-count")) || 0;
                animateCounter(el, target);
                counterObserver.unobserve(el);
            }
        });
    }, { threshold: 0.3 });

    document.querySelectorAll("[data-count]").forEach(el => {
        counterObserver.observe(el);
    });

    function animateCounter(el, target) {
        const duration = 1500;
        const startTime = performance.now();

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 4);
            const current = Math.floor(target * eased);
            el.textContent = current;
            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                el.textContent = target;
            }
        }
        requestAnimationFrame(update);
    }

    // === FLOATING PARTICLES (Desktop only) ===
    const particleContainer = document.getElementById("floatingParticles");
    if (particleContainer && window.innerWidth > 768) {
        for (let i = 0; i < 20; i++) {
            const p = document.createElement("div");
            p.className = "floating-particle";
            p.style.left = Math.random() * 100 + "%";
            p.style.animationDuration = (15 + Math.random() * 25) + "s";
            p.style.animationDelay = -(Math.random() * 20) + "s";
            const size = (2 + Math.random() * 4) + "px";
            p.style.width = size;
            p.style.height = size;
            p.style.opacity = (0.15 + Math.random() * 0.2).toString();
            particleContainer.appendChild(p);
        }
    }

    // === SMOOTH REVEAL ON SCROLL ===
    const revealElements = document.querySelectorAll(".reveal-up, .reveal-right, .reveal-left, .reveal-fade, .reveal-scale");
    if (revealElements.length > 0) {
        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("reveal-visible");
                }
            });
        }, { threshold: 0.1 });
        revealElements.forEach(el => revealObserver.observe(el));
    }

    // === AUTO-DISMISS ALERTS ===
    document.querySelectorAll(".alert-dismissible").forEach(alert => {
        setTimeout(() => {
            try {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                if (bsAlert) bsAlert.close();
            } catch(e) {
                alert.style.display = "none";
            }
        }, 6000);
    });

    console.log("DeepFake Shield initialized ✓");
});