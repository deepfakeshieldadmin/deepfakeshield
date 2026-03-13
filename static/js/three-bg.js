/* ═══════════════════════════════════════════════════════════
   DEEP FAKE SHIELD — THREE.JS 3D ANIMATED BACKGROUND
   Floating particles and geometric shapes
   ═══════════════════════════════════════════════════════════ */

(function () {
    const canvas = document.getElementById('three-bg-canvas');
    if (!canvas || typeof THREE === 'undefined') return;

    // Skip on landing page
    if (window.location.pathname === '/' || window.location.pathname === '') return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });

    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0);

    camera.position.z = 30;

    // ─── CREATE PARTICLES ────────────────────────────────
    const particleCount = 150;
    const particleGeometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    const colorOptions = [
        new THREE.Color(0x007bff),  // Blue
        new THREE.Color(0x6f42c1),  // Purple
        new THREE.Color(0x00d4ff),  // Cyan
        new THREE.Color(0x28a745),  // Green
    ];

    for (let i = 0; i < particleCount; i++) {
        positions[i * 3] = (Math.random() - 0.5) * 60;
        positions[i * 3 + 1] = (Math.random() - 0.5) * 60;
        positions[i * 3 + 2] = (Math.random() - 0.5) * 60;

        const color = colorOptions[Math.floor(Math.random() * colorOptions.length)];
        colors[i * 3] = color.r;
        colors[i * 3 + 1] = color.g;
        colors[i * 3 + 2] = color.b;
    }

    particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    particleGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const particleMaterial = new THREE.PointsMaterial({
        size: 0.15,
        vertexColors: true,
        transparent: true,
        opacity: 0.6,
        blending: THREE.AdditiveBlending,
    });

    const particles = new THREE.Points(particleGeometry, particleMaterial);
    scene.add(particles);

    // ─── CREATE FLOATING GEOMETRIC SHAPES ────────────────
    const shapes = [];

    // Wireframe octahedrons
    for (let i = 0; i < 5; i++) {
        const geometry = new THREE.OctahedronGeometry(Math.random() * 2 + 0.5);
        const material = new THREE.MeshBasicMaterial({
            color: colorOptions[Math.floor(Math.random() * colorOptions.length)],
            wireframe: true,
            transparent: true,
            opacity: 0.15,
        });
        const mesh = new THREE.Mesh(geometry, material);

        mesh.position.set(
            (Math.random() - 0.5) * 40,
            (Math.random() - 0.5) * 40,
            (Math.random() - 0.5) * 20
        );

        mesh.userData = {
            rotSpeed: {
                x: (Math.random() - 0.5) * 0.01,
                y: (Math.random() - 0.5) * 0.01,
                z: (Math.random() - 0.5) * 0.01,
            },
            floatSpeed: Math.random() * 0.005 + 0.002,
            floatOffset: Math.random() * Math.PI * 2,
        };

        scene.add(mesh);
        shapes.push(mesh);
    }

    // Wireframe torus knots
    for (let i = 0; i < 3; i++) {
        const geometry = new THREE.TorusKnotGeometry(1, 0.3, 64, 8);
        const material = new THREE.MeshBasicMaterial({
            color: colorOptions[Math.floor(Math.random() * colorOptions.length)],
            wireframe: true,
            transparent: true,
            opacity: 0.08,
        });
        const mesh = new THREE.Mesh(geometry, material);

        mesh.position.set(
            (Math.random() - 0.5) * 50,
            (Math.random() - 0.5) * 50,
            (Math.random() - 0.5) * 30 - 10
        );

        mesh.userData = {
            rotSpeed: {
                x: (Math.random() - 0.5) * 0.005,
                y: (Math.random() - 0.5) * 0.005,
                z: (Math.random() - 0.5) * 0.005,
            },
            floatSpeed: Math.random() * 0.003 + 0.001,
            floatOffset: Math.random() * Math.PI * 2,
        };

        scene.add(mesh);
        shapes.push(mesh);
    }

    // ─── CONNECTING LINES ────────────────────────────────
    const lineGeometry = new THREE.BufferGeometry();
    const linePositions = new Float32Array(100 * 6);
    lineGeometry.setAttribute('position', new THREE.BufferAttribute(linePositions, 3));

    const lineMaterial = new THREE.LineBasicMaterial({
        color: 0x007bff,
        transparent: true,
        opacity: 0.05,
    });

    const lines = new THREE.LineSegments(lineGeometry, lineMaterial);
    scene.add(lines);

    // ─── MOUSE INTERACTION ───────────────────────────────
    let mouseX = 0, mouseY = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = (e.clientX / window.innerWidth) * 2 - 1;
        mouseY = -(e.clientY / window.innerHeight) * 2 + 1;
    });

    // ─── ANIMATION LOOP ─────────────────────────────────
    let time = 0;

    function animate() {
        requestAnimationFrame(animate);
        time += 0.01;

        // Rotate particles
        particles.rotation.y += 0.0005;
        particles.rotation.x += 0.0002;

        // Mouse influence on camera
        camera.position.x += (mouseX * 3 - camera.position.x) * 0.02;
        camera.position.y += (mouseY * 3 - camera.position.y) * 0.02;
        camera.lookAt(scene.position);

        // Animate shapes
        shapes.forEach(shape => {
            shape.rotation.x += shape.userData.rotSpeed.x;
            shape.rotation.y += shape.userData.rotSpeed.y;
            shape.rotation.z += shape.userData.rotSpeed.z;

            shape.position.y += Math.sin(time + shape.userData.floatOffset) * shape.userData.floatSpeed;
        });

        // Update connecting lines between nearby particles
        const posArray = particleGeometry.attributes.position.array;
        let lineIndex = 0;
        const maxDist = 10;

        for (let i = 0; i < Math.min(particleCount, 30); i++) {
            for (let j = i + 1; j < Math.min(particleCount, 30); j++) {
                if (lineIndex >= 100) break;

                const dx = posArray[i * 3] - posArray[j * 3];
                const dy = posArray[i * 3 + 1] - posArray[j * 3 + 1];
                const dz = posArray[i * 3 + 2] - posArray[j * 3 + 2];
                const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

                if (dist < maxDist) {
                    linePositions[lineIndex * 6] = posArray[i * 3];
                    linePositions[lineIndex * 6 + 1] = posArray[i * 3 + 1];
                    linePositions[lineIndex * 6 + 2] = posArray[i * 3 + 2];
                    linePositions[lineIndex * 6 + 3] = posArray[j * 3];
                    linePositions[lineIndex * 6 + 4] = posArray[j * 3 + 1];
                    linePositions[lineIndex * 6 + 5] = posArray[j * 3 + 2];
                    lineIndex++;
                }
            }
        }

        lineGeometry.attributes.position.needsUpdate = true;

        renderer.render(scene, camera);
    }

    animate();

    // ─── RESIZE HANDLER ──────────────────────────────────
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
})();