document.addEventListener("DOMContentLoaded", function () {
    const body = document.body;
    const toggleBtn = document.getElementById("toggleThemeModeBtn");
    const themeSwatches = document.querySelectorAll(".theme-swatch");

    function applyTheme(mode) {
        if (mode === "light") {
            body.classList.add("simple-light");
            localStorage.setItem("simpleTheme", "light");
        } else {
            body.classList.remove("simple-light");
            localStorage.setItem("simpleTheme", "dark");
        }
    }

    const saved = localStorage.getItem("simpleTheme") || "dark";
    applyTheme(saved);

    if (toggleBtn) {
        toggleBtn.addEventListener("click", function () {
            if (body.classList.contains("simple-light")) {
                applyTheme("dark");
            } else {
                applyTheme("light");
            }
        });
    }

    themeSwatches.forEach(function (sw) {
        sw.addEventListener("click", function () {
            // Disable fake multi-theme behavior for now
            if (sw.dataset.theme === "theme-minimal-light") {
                applyTheme("light");
            } else {
                applyTheme("dark");
            }
        });
    });
});