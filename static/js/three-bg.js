/* ═══════════════════════════════════════════════════════════════
   DeepFake Shield — 3D Particle Network Background
   Lightweight canvas-based with depth simulation
   ═══════════════════════════════════════════════════════════════ */
(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', initBackground);

    function initBackground() {
        // Only run on pages that have the hero section
        var hero = document.querySelector('.home-hero, .hero-bg-effects');
        if (!hero) return;

        var canvas = document.createElement('canvas');
        canvas.id = 'network-3d-canvas';
        canvas.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;opacity:0.6;';

        var parent = hero.querySelector('.hero-bg-effects') || hero;
        parent.style.position = 'relative';
        parent.insertBefore(canvas, parent.firstChild);

        var ctx = canvas.getContext('2d');
        if (!ctx) return;

        var w, h, nodes = [], mouseX = -999, mouseY = -999;
        var maxDist = 160;
        var count = 0;

        function resize() {
            w = canvas.width = canvas.offsetWidth || window.innerWidth;
            h = canvas.height = canvas.offsetHeight || window.innerHeight;
            count = Math.min(60, Math.floor((w * h) / 15000));
            createNodes();
        }

        function createNodes() {
            nodes = [];
            for (var i = 0; i < count; i++) {
                nodes.push({
                    x: Math.random() * w,
                    y: Math.random() * h,
                    z: Math.random() * 200 + 50, // depth
                    vx: (Math.random() - 0.5) * 0.4,
                    vy: (Math.random() - 0.5) * 0.4,
                    vz: (Math.random() - 0.5) * 0.3,
                    baseSize: Math.random() * 2.5 + 1,
                });
            }
        }

        function project(node) {
            // Simple perspective projection
            var fov = 500;
            var scale = fov / (fov + node.z);
            return {
                x: node.x * scale + (w * (1 - scale)) / 2,
                y: node.y * scale + (h * (1 - scale)) / 2,
                scale: scale,
                size: node.baseSize * scale
            };
        }

        resize();
        window.addEventListener('resize', function () {
            clearTimeout(window._bgResizeTimer);
            window._bgResizeTimer = setTimeout(resize, 200);
        });

        canvas.parentElement.addEventListener('mousemove', function (e) {
            var rect = canvas.getBoundingClientRect();
            mouseX = e.clientX - rect.left;
            mouseY = e.clientY - rect.top;
        }, { passive: true });

        canvas.parentElement.addEventListener('mouseleave', function () {
            mouseX = -999;
            mouseY = -999;
        });

        var isDark = true;
        window.addEventListener('themechange', function (e) {
            isDark = e.detail.theme === 'dark';
        });
        isDark = document.documentElement.getAttribute('data-theme') !== 'light';

        var time = 0;

        function draw() {
            ctx.clearRect(0, 0, w, h);
            time += 0.005;

            var rgb = isDark ? '102,126,234' : '80,100,200';
            var rgb2 = isDark ? '118,75,162' : '140,80,180';

            // Update nodes
            for (var i = 0; i < nodes.length; i++) {
                var n = nodes[i];
                n.x += n.vx + Math.sin(time + i) * 0.15;
                n.y += n.vy + Math.cos(time + i * 0.7) * 0.15;
                n.z += n.vz;

                // Bounce
                if (n.x < 0 || n.x > w) n.vx *= -1;
                if (n.y < 0 || n.y > h) n.vy *= -1;
                if (n.z < 10 || n.z > 250) n.vz *= -1;

                // Mouse repulsion
                if (mouseX > 0) {
                    var ddx = n.x - mouseX;
                    var ddy = n.y - mouseY;
                    var dd = Math.sqrt(ddx * ddx + ddy * ddy);
                    if (dd < 120 && dd > 0) {
                        n.x += (ddx / dd) * 1.5;
                        n.y += (ddy / dd) * 1.5;
                    }
                }

                // Clamp
                n.x = Math.max(0, Math.min(w, n.x));
                n.y = Math.max(0, Math.min(h, n.y));
            }

            // Sort by z (far to near) for depth
            nodes.sort(function (a, b) { return b.z - a.z; });

            // Draw connections
            for (var i = 0; i < nodes.length; i++) {
                var pi = project(nodes[i]);
                for (var j = i + 1; j < nodes.length; j++) {
                    var pj = project(nodes[j]);
                    var dx = pi.x - pj.x;
                    var dy = pi.y - pj.y;
                    var dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < maxDist) {
                        var alpha = (1 - dist / maxDist) * 0.2 * Math.min(pi.scale, pj.scale);
                        ctx.beginPath();
                        ctx.moveTo(pi.x, pi.y);
                        ctx.lineTo(pj.x, pj.y);
                        ctx.strokeStyle = 'rgba(' + rgb + ',' + alpha + ')';
                        ctx.lineWidth = 0.6 * Math.min(pi.scale, pj.scale);
                        ctx.stroke();
                    }
                }
            }

            // Draw nodes
            for (var i = 0; i < nodes.length; i++) {
                var p = project(nodes[i]);
                var glow = (Math.sin(time * 2 + i) + 1) * 0.15 + 0.3;

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(' + (i % 2 === 0 ? rgb : rgb2) + ',' + (glow * p.scale) + ')';
                ctx.fill();

                // Glow effect for larger nodes
                if (p.size > 2) {
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.size * 2.5, 0, Math.PI * 2);
                    ctx.fillStyle = 'rgba(' + rgb + ',' + (glow * 0.08 * p.scale) + ')';
                    ctx.fill();
                }
            }

            // Mouse glow
            if (mouseX > 0 && mouseY > 0) {
                var grad = ctx.createRadialGradient(mouseX, mouseY, 0, mouseX, mouseY, 100);
                grad.addColorStop(0, 'rgba(' + rgb + ',0.12)');
                grad.addColorStop(1, 'rgba(' + rgb + ',0)');
                ctx.fillStyle = grad;
                ctx.fillRect(mouseX - 100, mouseY - 100, 200, 200);
            }

            requestAnimationFrame(draw);
        }

        draw();

        // Pause when not visible
        document.addEventListener('visibilitychange', function () {
            if (!document.hidden) requestAnimationFrame(draw);
        });
    }
})();