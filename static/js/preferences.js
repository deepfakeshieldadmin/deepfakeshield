document.addEventListener("DOMContentLoaded", function () {
    const panel = document.getElementById("preferencesPanel");
    const overlay = document.getElementById("preferencesOverlay");
    const openBtn = document.getElementById("openPreferencesBtn");
    const closeBtn = document.getElementById("closePreferencesBtn");
    const navBtn = document.getElementById("navPreferencesBtn");

    function openPanel() {
        if (panel) panel.classList.add("open");
        if (overlay) overlay.classList.add("show");
    }

    function closePanel() {
        if (panel) panel.classList.remove("open");
        if (overlay) overlay.classList.remove("show");
    }

    if (openBtn) openBtn.addEventListener("click", openPanel);
    if (closeBtn) closeBtn.addEventListener("click", closePanel);
    if (navBtn) navBtn.addEventListener("click", openPanel);
    if (overlay) overlay.addEventListener("click", closePanel);

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            closePanel();
        }
    });
});