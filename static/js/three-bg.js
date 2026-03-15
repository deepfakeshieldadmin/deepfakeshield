/* ============================================
   DEEPFAKE SHIELD — THREE-BG JS
   Lightweight 3D Floating Shapes (No Three.js)
   Pure CSS 3D transforms + JS animation
   ============================================ */

document.addEventListener("DOMContentLoaded", () => {
    // Only run on pages that have the container
    const heroSection = document.querySelector(".premium-hero-section, .landing-hero");
    if (!heroSection) return;

    // Don't run on mobile
    if (window.innerWidth < 768) return;

    const container = document.createElement("div");
    container.className = "three-bg-container";
    container.setAttribute("aria-hidden", "true");
    heroSection.appendChild(container);

    // Inject styles
    const style = document.createElement("style");
    style.textContent = `
        .three-bg-container {
            position: absolute;
            inset: 0;
            overflow: hidden;
            pointer-events: none;
            z-index: 1;
            perspective: 1200px;
        }

        .three-shape {
            position: absolute;
            opacity: 0.06;
            animation: threeDrift linear infinite;
            will-change: transform;
        }

        .shape-cube {
            width: 40px;
            height: 40px;
            transform-style: preserve-3d;
            animation-name: threeCubeRotate;
        }

        .shape-cube .face {
            position: absolute;
            width: 40px;
            height: 40px;
            border: 1px solid var(--accent, #00d2ff);
            border-radius: 4px;
        }

        .shape-cube .face-front  { transform: translateZ(20px); }
        .shape-cube .face-back   { transform: rotateY(180deg) translateZ(20px); }
        .shape-cube .face-left   { transform: rotateY(-90deg) translateZ(20px); }
        .shape-cube .face-right  { transform: rotateY(90deg) translateZ(20px); }
        .shape-cube .face-top    { transform: rotateX(90deg) translateZ(20px); }
        .shape-cube .face-bottom { transform: rotateX(-90deg) translateZ(20px); }

        .shape-octahedron {
            width: 0;
            height: 0;
            border-left: 20px solid transparent;
            border-right: 20px solid transparent;
            border-bottom: 35px solid rgba(122, 92, 255, 0.15);
            animation-name: threeDiaRotate;
        }

        .shape-ring {
            width: 50px;
            height: 50px;
            border: 2px solid rgba(0, 210, 255, 0.12);
            border-radius: 50%;
            animation-name: threeRingRotate;
        }

        .shape-cross {
            width: 30px;
            height: 30px;
            position: relative;
            animation-name: threeCrossRotate;
        }

        .shape-cross::before,
        .shape-cross::after {
            content: '';
            position: absolute;
            background: rgba(33, 208, 122, 0.12);
            border-radius: 2px;
        }
        .shape-cross::before {
            width: 100%;
            height: 4px;
            top: 50%;
            transform: translateY(-50%);
        }
        .shape-cross::after {
            width: 4px;
            height: 100%;
            left: 50%;
            transform: translateX(-50%);
        }

        .shape-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: radial-gradient(circle, var(--accent, #00d2ff), transparent);
            animation-name: threeDotPulse;
        }

        @keyframes threeCubeRotate {
            0%   { transform: translate(0, 0) rotateX(0) rotateY(0) rotateZ(0); }
            100% { transform: translate(50px, -80px) rotateX(360deg) rotateY(360deg) rotateZ(180deg); }
        }

        @keyframes threeDiaRotate {
            0%   { transform: translate(0, 0) rotateZ(0) scale(1); }
            50%  { transform: translate(30px, -50px) rotateZ(180deg) scale(1.2); }
            100% { transform: translate(-20px, -100px) rotateZ(360deg) scale(1); }
        }

        @keyframes threeRingRotate {
            0%   { transform: translate(0, 0) rotateX(0) rotateY(0); }
            100% { transform: translate(-40px, -60px) rotateX(360deg) rotateY(180deg); }
        }

        @keyframes threeCrossRotate {
            0%   { transform: translate(0, 0) rotate(0); }
            100% { transform: translate(60px, -90px) rotate(360deg); }
        }

        @keyframes threeDotPulse {
            0%, 100% { transform: scale(1); opacity: .06; }
            50%      { transform: scale(2); opacity: .12; }
        }

        @keyframes threeDrift {
            0%   { transform: translate(0, 0); }
            100% { transform: translate(var(--dx, 30px), var(--dy, -80px)); }
        }
    `;
    document.head.appendChild(style);

    const shapes = ['cube', 'octahedron', 'ring', 'cross', 'dot'];

    for (let i = 0; i < 12; i++) {
        const type = shapes[Math.floor(Math.random() * shapes.length)];
        const el = document.createElement("div");
        el.className = `three-shape shape-${type}`;

        // Random position
        el.style.left = `${5 + Math.random() * 85}%`;
        el.style.top = `${5 + Math.random() * 85}%`;

        // Random animation
        el.style.animationDuration = `${15 + Math.random() * 30}s`;
        el.style.animationDelay = `${-Math.random() * 20}s`;
        el.style.setProperty('--dx', `${(Math.random() - 0.5) * 100}px`);
        el.style.setProperty('--dy', `${-50 - Math.random() * 100}px`);

        // If cube, add faces
        if (type === 'cube') {
            const faces = ['front', 'back', 'left', 'right', 'top', 'bottom'];
            faces.forEach(f => {
                const face = document.createElement("div");
                face.className = `face face-${f}`;
                el.appendChild(face);
            });
        }

        container.appendChild(el);
    }

    // Parallax on mouse move
    document.addEventListener("mousemove", (e) => {
        const x = (e.clientX / window.innerWidth - 0.5) * 15;
        const y = (e.clientY / window.innerHeight - 0.5) * 15;
        container.style.transform = `translate(${x}px, ${y}px)`;
    });

    console.log("3D background shapes initialized ✓");
});