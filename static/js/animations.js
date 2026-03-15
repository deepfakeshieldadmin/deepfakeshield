/* ============================================
   DEEPFAKE SHIELD — ANIMATIONS JS
   ============================================ */

document.addEventListener("DOMContentLoaded", () => {
    // === INTERSECTION OBSERVER REVEALS ===
    const elements = document.querySelectorAll(
        ".reveal-up, .reveal-right, .reveal-left, .reveal-fade, .reveal-scale"
    );

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("reveal-visible");
            }
        });
    }, { threshold: 0.1, rootMargin: "0px 0px -40px 0px" });

    elements.forEach(el => observer.observe(el));

    // === PARALLAX EFFECT ON SCROLL ===
    const parallaxElements = document.querySelectorAll("[data-parallax]");
    if (parallaxElements.length > 0) {
        window.addEventListener("scroll", () => {
            const scrollY = window.scrollY;
            parallaxElements.forEach(el => {
                const speed = parseFloat(el.dataset.parallax) || 0.3;
                el.style.transform = `translateY(${scrollY * speed}px)`;
            });
        }, { passive: true });
    }

    // === TILT EFFECT ON CARDS ===
    document.querySelectorAll("[data-tilt]").forEach(card => {
        card.addEventListener("mousemove", (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = ((y - centerY) / centerY) * -4;
            const rotateY = ((x - centerX) / centerX) * 4;
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
        });

        card.addEventListener("mouseleave", () => {
            card.style.transform = "perspective(1000px) rotateX(0) rotateY(0) scale(1)";
        });
    });

    // === TEXT SCRAMBLE EFFECT ===
    document.querySelectorAll("[data-scramble]").forEach(el => {
        const originalText = el.textContent;
        const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
        let iteration = 0;

        const scrambleObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    iteration = 0;
                    const interval = setInterval(() => {
                        el.textContent = originalText
                            .split("")
                            .map((letter, index) => {
                                if (index < iteration) return originalText[index];
                                return chars[Math.floor(Math.random() * chars.length)];
                            })
                            .join("");

                        if (iteration >= originalText.length) clearInterval(interval);
                        iteration += 1 / 2;
                    }, 30);
                    scrambleObserver.unobserve(el);
                }
            });
        }, { threshold: 0.5 });

        scrambleObserver.observe(el);
    });

    // === MAGNETIC BUTTON EFFECT ===
    document.querySelectorAll(".btn-glow, .btn-hero-primary").forEach(btn => {
        btn.addEventListener("mousemove", (e) => {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            btn.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px)`;
        });
        btn.addEventListener("mouseleave", () => {
            btn.style.transform = "";
        });
    });
});