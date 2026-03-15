/* ============================================
   DEEPFAKE SHIELD — I18N JS
   ============================================ */

document.addEventListener("DOMContentLoaded", () => {
    const translations = {
        en: { nav_home:"Home", nav_dashboard:"Dashboard", nav_detect:"Detect", nav_about:"About", nav_personalize:"Personalize", nav_login:"Login", nav_signup:"Sign Up" },
        hi: { nav_home:"होम", nav_dashboard:"डैशबोर्ड", nav_detect:"जांच", nav_about:"परिचय", nav_personalize:"पसंद", nav_login:"लॉगिन", nav_signup:"साइन अप" },
        mr: { nav_home:"मुख्यपृष्ठ", nav_dashboard:"डॅशबोर्ड", nav_detect:"तपासणी", nav_about:"माहिती", nav_personalize:"वैयक्तिकरण", nav_login:"लॉगिन", nav_signup:"नोंदणी" },
        te: { nav_home:"హోమ్", nav_dashboard:"డాష్‌బోర్డ్", nav_detect:"స్కాన్", nav_about:"గురించి", nav_personalize:"అభిరుచులు", nav_login:"లాగిన్", nav_signup:"సైన్ అప్" },
        ta: { nav_home:"முகப்பு", nav_dashboard:"டாஷ்போர்டு", nav_detect:"கண்டறிதல்", nav_about:"பற்றி", nav_personalize:"தனிப்பயன்", nav_login:"உள்நுழை", nav_signup:"பதிவு" },
        kn: { nav_home:"ಮುಖಪುಟ", nav_dashboard:"ಡ್ಯಾಶ್‌ಬೋರ್ಡ್", nav_detect:"ಪರಿಶೀಲನೆ", nav_about:"ಬಗ್ಗೆ", nav_personalize:"ಆಯ್ಕೆಗಳು", nav_login:"ಲಾಗಿನ್", nav_signup:"ಸೈನ್ ಅಪ್" },
        fr: { nav_home:"Accueil", nav_dashboard:"Tableau de bord", nav_detect:"Détection", nav_about:"À propos", nav_personalize:"Préférences", nav_login:"Connexion", nav_signup:"Inscription" },
        ja: { nav_home:"ホーム", nav_dashboard:"ダッシュボード", nav_detect:"検出", nav_about:"概要", nav_personalize:"設定", nav_login:"ログイン", nav_signup:"登録" }
    };

    function applyLanguage(lang) {
        const dict = translations[lang] || translations.en;
        document.querySelectorAll("[data-translate]").forEach(el => {
            const key = el.getAttribute("data-translate");
            if (dict[key]) el.textContent = dict[key];
        });
    }

    const savedLang = localStorage.getItem("siteLanguage") || "en";
    applyLanguage(savedLang);

    window.addEventListener("languageChanged", (e) => {
        applyLanguage(e.detail.language);
    });

    // Landing language selector
    const landingLang = document.getElementById("landingLanguage");
    if (landingLang) {
        landingLang.value = savedLang;
        landingLang.addEventListener("change", () => {
            localStorage.setItem("siteLanguage", landingLang.value);
            applyLanguage(landingLang.value);
        });
    }
});