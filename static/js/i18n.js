/* ═══════════════════════════════════════════════════════════
   DEEP FAKE SHIELD — INTERNATIONALIZATION (i18n)
   Multi-language support via data-translate attributes
   ═══════════════════════════════════════════════════════════ */

const translations = {
    en: {
        // Navbar
        nav_home: "Home", nav_dashboard: "Dashboard", nav_scan: "Scan",
        nav_learn: "Learn", nav_about: "About", nav_privacy: "Privacy Policy",
        nav_login: "Login", nav_signup: "Sign Up",
        // Hero
        ai_powered: "AI-Powered Media Verification",
        protect_yourself: "Protect Yourself from",
        digital_deception: "Digital Deception",
        hero_desc: "Deep Fake Shield uses advanced heuristic analysis to verify the authenticity of images, videos, audio, and text — helping you identify AI-generated and manipulated media in seconds.",
        get_started: "Get Started Free", login: "Login",
        go_dashboard: "Go to Dashboard",
        // Features
        detection_capabilities: "Detection Capabilities",
        features_subtitle: "Four powerful detection engines working together to verify media authenticity",
        image_detection: "Image Detection", video_detection: "Video Detection",
        audio_detection: "Audio Detection", text_detection: "Text Detection",
        scan_now: "Scan Now",
        image_detection_desc: "Analyze photos for AI generation, manipulation, EXIF data, face count, and noise patterns",
        video_detection_desc: "Frame-by-frame analysis to detect deepfake videos and manipulated footage",
        audio_detection_desc: "Detect synthetic voices, clipping, spectral anomalies, and AI-generated audio",
        text_detection_desc: "Identify AI-written content by analyzing patterns, repetition, and language style",
        // How it works
        how_it_works: "How It Works",
        how_subtitle: "Simple, fast, and accurate media verification",
        step_upload: "Upload", step_upload_desc: "Upload your media file or paste text",
        step_analyze: "Analyze", step_analyze_desc: "AI engines process & scan the media",
        step_results: "Results", step_results_desc: "Get authenticity score & detailed report",
        step_protect: "Protect", step_protect_desc: "Make informed decisions about media",
        // CTA
        ready_to_verify: "Ready to Verify Your Media?",
        cta_desc: "Start detecting deepfakes and manipulated content today — it's completely free.",
        create_account: "Create Free Account",
        // Dashboard
        welcome: "Welcome back,", dashboard_desc: "Monitor your scans, detect threats, and verify media authenticity.",
        new_scan: "New Scan", total_scans: "Total Scans", image_scans: "Image Scans",
        video_scans: "Video Scans", threats_detected: "Threats Detected",
        quick_actions: "Quick Actions",
        scan_image: "Scan Image", scan_video: "Scan Video",
        scan_audio: "Scan Audio", scan_text: "Scan Text",
        scan_image_desc: "Upload & analyze photos", scan_video_desc: "Analyze video frames",
        scan_audio_desc: "Detect synthetic audio", scan_text_desc: "Detect AI-written text",
        recent_images: "Recent Image Scans", recent_videos: "Recent Video Scans",
        recent_audio: "Recent Audio Scans", recent_text: "Recent Text Scans",
        no_scans_yet: "No scans yet", new: "New",
        // Upload pages
        image_scan_title: "Image Authenticity Scan",
        image_scan_desc: "Upload an image to analyze for AI generation, manipulation, and metadata verification",
        drag_drop: "Drag & Drop your image here",
        or_browse: "or click to browse files", max_size: "Maximum file size: 20MB",
        analyze_image: "Analyze Image", analyzing: "Analyzing Image...",
        please_wait: "Please wait while we process your file",
        exif_check: "EXIF Verification", face_detection: "Face Detection", noise_analysis: "Noise Analysis",
        video_scan_title: "Video Authenticity Scan",
        video_scan_desc: "Upload a video to analyze individual frames for deepfake detection",
        analyze_video: "Analyze Video",
        audio_scan_title: "Audio Authenticity Scan",
        audio_scan_desc: "Upload an audio file to analyze for synthetic voice, clipping, and spectral anomalies",
        analyze_audio: "Analyze Audio",
        text_scan_title: "Text Authenticity Scan",
        text_scan_desc: "Paste text to analyze for AI-generation patterns, repetition, and language anomalies",
        paste_text: "Paste your text below", analyze_text: "Analyze Text",
        // Results
        analysis_result: "Analysis Result", scan_another: "Scan Another",
        authenticity_score: "Authenticity Score",
        analysis_breakdown: "Analysis Breakdown", exif_metadata: "EXIF Metadata",
        detailed_explanation: "Detailed Explanation",
        no_exif: "No EXIF metadata found in this image",
        scan_another_image: "Scan Another Image", back_dashboard: "Back to Dashboard",
        learn_more: "Learn More",
        // Auth
        login_title: "Sign In", login_subtitle: "Enter your credentials to access your account",
        signup_title: "Create Account", signup_subtitle: "Fill in your details to get started",
        sign_in: "Sign In", remember_me: "Remember me",
        no_account: "Don't have an account?", sign_up_link: "Sign Up",
        have_account: "Already have an account?", sign_in_link: "Sign In",
        // Landing
        enter_shield: "Enter Shield",
        // Footer
        footer_desc: "Advanced AI-powered media authenticity verification system.",
        footer_navigation: "Navigation", footer_detection: "Detection", footer_technology: "Technology",
        diploma_project: "Diploma Final Year Project 2024-25",
        academic_excellence: "Academic Excellence",
        // Cookie
        cookie_title: "Cookie Notice",
        cookie_desc: "We use cookies and localStorage to save your preferences.",
        cookie_accept: "Accept", cookie_decline: "Decline",
    },

    hi: {
        nav_home: "होम", nav_dashboard: "डैशबोर्ड", nav_scan: "स्कैन",
        nav_learn: "सीखें", nav_about: "जानकारी", nav_login: "लॉगिन", nav_signup: "साइन अप",
        ai_powered: "AI-संचालित मीडिया सत्यापन",
        protect_yourself: "खुद को बचाएं", digital_deception: "डिजिटल धोखे से",
        hero_desc: "डीप फेक शील्ड उन्नत विश्लेषण का उपयोग करके छवियों, वीडियो, ऑडियो और टेक्स्ट की प्रामाणिकता सत्यापित करता है।",
        get_started: "मुफ्त शुरू करें", login: "लॉगिन",
        go_dashboard: "डैशबोर्ड पर जाएं",
        detection_capabilities: "पहचान क्षमताएं",
        image_detection: "छवि पहचान", video_detection: "वीडियो पहचान",
        audio_detection: "ऑडियो पहचान", text_detection: "टेक्स्ट पहचान",
        scan_now: "अभी स्कैन करें",
        welcome: "वापसी पर स्वागत है,", new_scan: "नया स्कैन",
        total_scans: "कुल स्कैन", threats_detected: "खतरे पाए गए",
        scan_image: "छवि स्कैन", scan_video: "वीडियो स्कैन",
        scan_audio: "ऑडियो स्कैन", scan_text: "टेक्स्ट स्कैन",
        enter_shield: "शील्ड में प्रवेश करें",
        analyze_image: "छवि विश्लेषण", analyze_video: "वीडियो विश्लेषण",
        analyze_audio: "ऑडियो विश्लेषण", analyze_text: "टेक्स्ट विश्लेषण",
        no_scans_yet: "अभी तक कोई स्कैन नहीं",
    },

    mr: {
        nav_home: "मुखपृष्ठ", nav_dashboard: "डॅशबोर्ड", nav_scan: "स्कॅन",
        nav_learn: "शिका", nav_about: "माहिती", nav_login: "लॉगिन", nav_signup: "साइन अप",
        ai_powered: "AI-चालित मीडिया पडताळणी",
        protect_yourself: "स्वतःचे रक्षण करा", digital_deception: "डिजिटल फसवणुकीपासून",
        get_started: "मोफत सुरू करा", login: "लॉगिन",
        welcome: "परत स्वागत आहे,",
        scan_image: "चित्र स्कॅन", scan_video: "व्हिडिओ स्कॅन",
        scan_audio: "ऑडिओ स्कॅन", scan_text: "मजकूर स्कॅन",
        enter_shield: "शील्ड मध्ये प्रवेश करा",
    },

    te: {
        nav_home: "హోమ్", nav_dashboard: "డాష్‌బోర్డ్", nav_scan: "స్కాన్",
        nav_learn: "నేర్చుకోండి", nav_about: "గురించి", nav_login: "లాగిన్", nav_signup: "సైన్ అప్",
        ai_powered: "AI-ఆధారిత మీడియా ధృవీకరణ",
        protect_yourself: "మిమ్మల్ని మీరు రక్షించుకోండి", digital_deception: "డిజిటల్ మోసం నుండి",
        get_started: "ఉచితంగా ప్రారంభించండి",
        welcome: "తిరిగి స్వాగతం,",
        enter_shield: "షీల్డ్ లోకి ప్రవేశించండి",
    },

    ta: {
        nav_home: "முகப்பு", nav_dashboard: "டாஷ்போர்டு", nav_scan: "ஸ்கேன்",
        nav_learn: "கற்றுக்கொள்", nav_about: "பற்றி", nav_login: "உள்நுழை", nav_signup: "பதிவு செய்",
        ai_powered: "AI-இயங்கும் ஊடக சரிபார்ப்பு",
        protect_yourself: "உங்களைக் காப்பாற்றுங்கள்", digital_deception: "டிஜிட்டல் ஏமாற்றத்திலிருந்து",
        get_started: "இலவசமாகத் தொடங்குங்கள்",
        welcome: "மீண்டும் வரவேற்கிறோம்,",
        enter_shield: "கவசத்தில் நுழையுங்கள்",
    },

    kn: {
        nav_home: "ಮುಖಪುಟ", nav_dashboard: "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್", nav_scan: "ಸ್ಕ್ಯಾನ್",
        nav_learn: "ಕಲಿಯಿರಿ", nav_about: "ಬಗ್ಗೆ", nav_login: "ಲಾಗಿನ್", nav_signup: "ಸೈನ್ ಅಪ್",
        ai_powered: "AI-ಚಾಲಿತ ಮಾಧ್ಯಮ ಪರಿಶೀಲನೆ",
        protect_yourself: "ನಿಮ್ಮನ್ನು ರಕ್ಷಿಸಿಕೊಳ್ಳಿ", digital_deception: "ಡಿಜಿಟಲ್ ವಂಚನೆಯಿಂದ",
        get_started: "ಉಚಿತವಾಗಿ ಪ್ರಾರಂಭಿಸಿ",
        welcome: "ಮತ್ತೆ ಸ್ವಾಗತ,",
        enter_shield: "ಶೀಲ್ಡ್ ಒಳಗೆ ಪ್ರವೇಶಿಸಿ",
    },

    fr: {
        nav_home: "Accueil", nav_dashboard: "Tableau de bord", nav_scan: "Scanner",
        nav_learn: "Apprendre", nav_about: "À propos", nav_login: "Connexion", nav_signup: "Inscription",
        ai_powered: "Vérification média par IA",
        protect_yourself: "Protégez-vous contre", digital_deception: "la tromperie numérique",
        hero_desc: "Deep Fake Shield utilise une analyse heuristique avancée pour vérifier l'authenticité des images, vidéos, audio et texte.",
        get_started: "Commencer gratuitement", login: "Connexion",
        go_dashboard: "Aller au tableau de bord",
        welcome: "Bienvenue,",
        scan_image: "Scanner Image", scan_video: "Scanner Vidéo",
        scan_audio: "Scanner Audio", scan_text: "Scanner Texte",
        enter_shield: "Entrer dans le bouclier",
        analyze_image: "Analyser l'image", analyze_video: "Analyser la vidéo",
    },

    ja: {
        nav_home: "ホーム", nav_dashboard: "ダッシュボード", nav_scan: "スキャン",
        nav_learn: "学ぶ", nav_about: "概要", nav_login: "ログイン", nav_signup: "登録",
        ai_powered: "AI搭載メディア認証",
        protect_yourself: "自分自身を守りましょう", digital_deception: "デジタル詐欺から",
        get_started: "無料で始める", login: "ログイン",
        welcome: "お帰りなさい、",
        scan_image: "画像スキャン", scan_video: "動画スキャン",
        scan_audio: "音声スキャン", scan_text: "テキストスキャン",
        enter_shield: "シールドに入る",
    },
};

let currentLanguage = localStorage.getItem('dfs-language') || 'en';

function changeLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('dfs-language', lang);

    const dict = translations[lang] || translations['en'];

    document.querySelectorAll('[data-translate]').forEach(el => {
        const key = el.getAttribute('data-translate');
        if (dict[key]) {
            el.textContent = dict[key];
        } else if (translations['en'][key]) {
            // Fallback to English
            el.textContent = translations['en'][key];
        }
    });

    if (typeof showToast === 'function') {
        const langNames = {
            en: 'English', hi: 'हिन्दी', mr: 'मराठी', te: 'తెలుగు',
            ta: 'தமிழ்', kn: 'ಕನ್ನಡ', fr: 'Français', ja: '日本語'
        };
        showToast(`Language: ${langNames[lang] || lang}`);
    }
}

// Apply saved language on load
document.addEventListener('DOMContentLoaded', function () {
    if (currentLanguage !== 'en') {
        changeLanguage(currentLanguage);
    }
});