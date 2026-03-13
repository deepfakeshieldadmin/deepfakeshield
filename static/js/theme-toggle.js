function applyThemePreset(themeName) {
    const body = document.body;

    body.classList.remove(
        'theme-tech-blue',
        'theme-matrix-green',
        'theme-cyber-purple',
        'theme-neon-sunset',
        'theme-minimal-light'
    );

    switch (themeName) {
        case 'matrix-green':
            body.classList.add('theme-matrix-green');
            break;
        case 'cyber-purple':
            body.classList.add('theme-cyber-purple');
            break;
        case 'neon-sunset':
            body.classList.add('theme-neon-sunset');
            break;
        case 'minimal-light':
            body.classList.add('theme-minimal-light');
            break;
        default:
            body.classList.add('theme-tech-blue');
    }

    localStorage.setItem('dfs-color-theme', themeName);
}

function setThemePreset(themeName) {
    applyThemePreset(themeName);
}

function toggleDarkMode() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme') || 'light';
    const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', nextTheme);
    localStorage.setItem('dfs-theme', nextTheme);

    const icon = document.getElementById('themeIcon');
    if (icon) {
        icon.className = nextTheme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars';
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const savedTheme = localStorage.getItem('dfs-theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    const icon = document.getElementById('themeIcon');
    if (icon) {
        icon.className = savedTheme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars';
    }

    const savedPreset = localStorage.getItem('dfs-color-theme') || 'tech-blue';
    applyThemePreset(savedPreset);
});