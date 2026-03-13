function showToast(message) {
    const toast = document.createElement('div');
    toast.innerText = message;
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '99999';
    toast.style.background = 'linear-gradient(135deg,#007bff,#6f42c1)';
    toast.style.color = '#fff';
    toast.style.padding = '12px 16px';
    toast.style.borderRadius = '12px';
    toast.style.boxShadow = '0 12px 30px rgba(0,123,255,0.25)';
    toast.style.fontWeight = '700';
    toast.style.fontSize = '0.9rem';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(12px)';
    toast.style.transition = 'all 0.25s ease';

    document.body.appendChild(toast);

    requestAnimationFrame(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
    });

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(12px)';
        setTimeout(() => toast.remove(), 250);
    }, 2000);
}