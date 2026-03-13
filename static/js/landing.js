/* ═══════════════════════════════════════════════════════════
   DEEP FAKE SHIELD — LANDING PAGE JAVASCRIPT
   Matrix rain, logo intro, animations
   ═══════════════════════════════════════════════════════════ */

// Check if should skip intro
const urlParams = new URLSearchParams(window.location.search);
const forceIntro = urlParams.get('intro') === 'true';
const hasVisited = localStorage.getItem('dfs-visited');

// ─── MATRIX RAIN ─────────────────────────────────────────
const matrixCanvas = document.getElementById('matrixCanvas');
const matrixCtx = matrixCanvas.getContext('2d');

function resizeMatrix() {
    matrixCanvas.width = window.innerWidth;
    matrixCanvas.height = window.innerHeight;
}
resizeMatrix();
window.addEventListener('resize', resizeMatrix);

const matrixChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%^&*()_+-=[]{}|;:,.<>?/~ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ';
const fontSize = 14;
let columns = Math.floor(matrixCanvas.width / fontSize);
let drops = Array(columns).fill(1);

function drawMatrix() {
    matrixCtx.fillStyle = 'rgba(10, 10, 10, 0.05)';
    matrixCtx.fillRect(0, 0, matrixCanvas.width, matrixCanvas.height);

    matrixCtx.fillStyle = '#0f0';
    matrixCtx.font = fontSize + 'px monospace';

    for (let i = 0; i < drops.length; i++) {
        const text = matrixChars[Math.floor(Math.random() * matrixChars.length)];

        // Vary green shades
        const brightness = Math.random();
        if (brightness > 0.8) {
            matrixCtx.fillStyle = '#fff';
        } else if (brightness > 0.5) {
            matrixCtx.fillStyle = '#0f0';
        } else {
            matrixCtx.fillStyle = '#003300';
        }

        matrixCtx.fillText(text, i * fontSize, drops[i] * fontSize);

        if (drops[i] * fontSize > matrixCanvas.height && Math.random() > 0.975) {
            drops[i] = 0;
        }
        drops[i]++;
    }
}

const matrixInterval = setInterval(drawMatrix, 50);

// ─── LOADING ANIMATION ──────────────────────────────────
const loadingBar = document.getElementById('loadingBar');
const loadingText = document.getElementById('loadingText');
const logoIntro = document.getElementById('logoIntro');
const landingContent = document.getElementById('landingContent');

const loadingMessages = [
    'Initializing Shield Systems...',
    'Loading AI Detection Engines...',
    'Preparing Image Analysis...',
    'Configuring Video Scanner...',
    'Setting Up Audio Processor...',
    'Calibrating Text Analyzer...',
    'Systems Ready!'
];

let loadProgress = 0;
let messageIndex = 0;

function updateLoading() {
    loadProgress += Math.random() * 8 + 2;
    if (loadProgress > 100) loadProgress = 100;

    loadingBar.style.width = loadProgress + '%';

    const newMsgIndex = Math.min(Math.floor(loadProgress / 15), loadingMessages.length - 1);
    if (newMsgIndex !== messageIndex) {
        messageIndex = newMsgIndex;
        loadingText.textContent = loadingMessages[messageIndex];
    }

    if (loadProgress >= 100) {
        clearInterval(loadingInterval);
        setTimeout(showContent, 800);
    }
}

// Skip intro if visited before (unless forced)
if (hasVisited && !forceIntro) {
    logoIntro.style.display = 'none';
    landingContent.style.display = 'block';
    animateStats();
    var loadingInterval = null;
} else {
    var loadingInterval = setInterval(updateLoading, 200);
}

function showContent() {
    logoIntro.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
    logoIntro.style.opacity = '0';
    logoIntro.style.transform = 'scale(1.1)';

    setTimeout(() => {
        logoIntro.style.display = 'none';
        landingContent.style.display = 'block';
        landingContent.style.opacity = '0';
        landingContent.style.transition = 'opacity 0.6s ease';
        setTimeout(() => {
            landingContent.style.opacity = '1';
            localStorage.setItem('dfs-visited', 'true');
            animateStats();
        }, 50);
    }, 800);
}

// ─── ANIMATE STATS COUNTING ─────────────────────────────
function animateStats() {
    document.querySelectorAll('.stat-number').forEach(el => {
        const target = parseInt(el.getAttribute('data-count')) || 0;
        let current = 0;
        const duration = 2000;
        const increment = target / (duration / 30);

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            el.textContent = Math.round(current);
        }, 30);
    });
}

// ─── LANGUAGE SELECTION ──────────────────────────────────
function selectLandingLanguage(lang) {
    localStorage.setItem('dfs-language', lang);

    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-lang') === lang) {
            btn.classList.add('active');
        }
    });
}

// ─── ENTER SITE ──────────────────────────────────────────
function enterSite() {
    localStorage.setItem('dfs-visited', 'true');
    window.location.href = '/home/';
}

// ─── RESIZE HANDLER ──────────────────────────────────────
window.addEventListener('resize', () => {
    resizeMatrix();
    columns = Math.floor(matrixCanvas.width / fontSize);
    drops = Array(columns).fill(1);
});