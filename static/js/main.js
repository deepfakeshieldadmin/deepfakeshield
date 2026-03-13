document.addEventListener('DOMContentLoaded', function () {
    const navbar = document.getElementById('mainNavbar');

    if (navbar) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 30) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }
});