/* ============================================
   DEEPFAKE SHIELD — LANDING JS (FIXED)
   Matrix Rain + Typed.js + Particles
   ============================================ */

document.addEventListener("DOMContentLoaded", () => {

    // === MATRIX RAIN — BRIGHTER AND VISIBLE ===
    const canvas = document.getElementById("matrixCanvas");
    if (canvas) {
        const ctx = canvas.getContext("2d");
        let width, height, columns, drops;
        const chars = "01アイウエオカキクケコサシスセソタチツテトABCDEFGHIJKLMNOPQRSTUVWXYZ<>/{}[]!@#$%^&*";
        const fontSize = 15;

        function resizeCanvas() {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
            columns = Math.floor(width / fontSize);
            drops = Array(columns).fill(1);
        }

        function draw() {
            // Slower fade = more visible trails
            ctx.fillStyle = "rgba(4, 8, 15, 0.04)";
            ctx.fillRect(0, 0, width, height);

            ctx.font = `${fontSize}px 'JetBrains Mono', monospace`;

            for (let i = 0; i < drops.length; i++) {
                const text = chars[Math.floor(Math.random() * chars.length)];

                // Bright green with high opacity
                const alpha = (0.5 + Math.random() * 0.5).toFixed(2);
                ctx.fillStyle = `rgba(0, 255, 135, ${alpha})`;

                ctx.fillText(text, i * fontSize, drops[i] * fontSize);

                if (drops[i] * fontSize > height && Math.random() > 0.975) {
                    drops[i] = 0;
                }
                drops[i]++;
            }
        }

        resizeCanvas();
        setInterval(draw, 45);
        window.addEventListener("resize", resizeCanvas);
    }

    // === TYPED.JS ===
    const typedEl = document.getElementById("landingTyped");
    if (typedEl && typeof Typed !== "undefined") {
        new Typed("#landingTyped", {
            strings: [
                "OpenCV Face Detection",
                "EXIF Metadata Analysis",
                "AI Artifact Detection",
                "Compression Noise Analysis",
                "Audio Signal Processing",
                "Text Heuristic Engine",
                "Video Frame Sampling",
                "PDF Report Generation",
                "Authenticity Scoring 0–100"
            ],
            typeSpeed: 40,
            backSpeed: 20,
            backDelay: 2000,
            loop: true,
            showCursor: true,
            cursorChar: "▌"
        });
    }

    // === LANDING PARTICLES ===
    const particleLayer = document.getElementById("landingParticles");
    if (particleLayer && window.innerWidth > 768) {
        const pStyle = document.createElement("style");
        pStyle.textContent = `
            @keyframes landingParticleFloat {
                0% { transform: translate(0, 0) scale(1); opacity: 0; }
                10% { opacity: .4; }
                50% { opacity: .2; }
                100% { transform: translate(0, -100vh) scale(0); opacity: 0; }
            }
        `;
        document.head.appendChild(pStyle);

        for (let i = 0; i < 30; i++) {
            const p = document.createElement("div");
            const size = 2 + Math.random() * 3;
            p.style.cssText = `
                position:absolute;
                width:${size}px;
                height:${size}px;
                background:rgba(0,255,135,${0.15 + Math.random() * 0.2});
                border-radius:50%;
                left:${Math.random() * 100}%;
                bottom: -10px;
                animation:landingParticleFloat ${12 + Math.random() * 20}s linear infinite;
                animation-delay:${-Math.random() * 15}s;
            `;
            particleLayer.appendChild(p);
        }
    }

    // === COUNTER ANIMATION ===
    const statNums = document.querySelectorAll(".feature-stat-num, .score-visual-num");
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const target = parseInt(el.getAttribute("data-count")) || 0;
                animateNum(el, target);
                counterObserver.unobserve(el);
            }
        });
    }, { threshold: 0.3 });

    statNums.forEach(el => counterObserver.observe(el));

    function animateNum(el, target) {
        const duration = 2000;
        const start = performance.now();
        function tick(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 4);
            el.textContent = Math.floor(target * eased);
            if (progress < 1) requestAnimationFrame(tick);
            else el.textContent = target;
        }
        requestAnimationFrame(tick);
    }

    // === LANGUAGE SELECTOR ===
    const landingLang = document.getElementById("landingLanguage");
    if (landingLang) {
        const savedLang = localStorage.getItem("siteLanguage") || "en";
        landingLang.value = savedLang;
        landingLang.addEventListener("change", () => {
            localStorage.setItem("siteLanguage", landingLang.value);
        });
    }

    console.log("Landing page initialized ✓");
});