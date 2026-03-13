/* ═══════════════════════════════════════════════════════════
   DEEP FAKE SHIELD — SCROLL ANIMATIONS
   Intersection Observer based reveal animations
   ═══════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {

    // ─── INTERSECTION OBSERVER FOR SCROLL ANIMATIONS ─────
    const animatedElements = document.querySelectorAll('.animate-on-scroll');

    if (animatedElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    // Add stagger delay
                    setTimeout(() => {
                        entry.target.classList.add('visible');
                    }, index * 50);
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        animatedElements.forEach(el => observer.observe(el));
    }

    // ─── PARALLAX EFFECT ON MOUSE MOVE ───────────────────
    const parallaxElements = document.querySelectorAll('[data-parallax]');
    if (parallaxElements.length > 0) {
        document.addEventListener('mousemove', (e) => {
            const x = (e.clientX / window.innerWidth - 0.5) * 2;
            const y = (e.clientY / window.innerHeight - 0.5) * 2;

            parallaxElements.forEach(el => {
                const speed = parseFloat(el.getAttribute('data-parallax')) || 1;
                el.style.transform = `translate(${x * speed * 10}px, ${y * speed * 10}px)`;
            });
        });
    }

    // ─── HOVER TILT EFFECT ON CARDS ──────────────────────
    const tiltCards = document.querySelectorAll('.feature-card, .action-card, .stat-card');
    tiltCards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = (y - centerY) / centerY * -5;
            const rotateY = (x - centerX) / centerX * 5;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-5px)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });

    // ─── MAGNETIC BUTTON EFFECT ──────────────────────────
    const magneticBtns = document.querySelectorAll('.btn-hero-primary, .enter-btn, .scan-submit-btn');
    magneticBtns.forEach(btn => {
        btn.addEventListener('mousemove', (e) => {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            btn.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px)`;
        });

        btn.addEventListener('mouseleave', () => {
            btn.style.transform = '';
        });
    });
});