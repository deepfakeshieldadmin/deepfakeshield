"""
DeepFake Shield — settings.py
Azure App Service + Render + Local compatible
"""
import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Security ──
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-key-change-in-production-use-50-chars')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# ── Allowed Hosts ──
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
_env_hosts = os.environ.get('ALLOWED_HOSTS', '')
if _env_hosts:
    ALLOWED_HOSTS += [h.strip() for h in _env_hosts.split(',') if h.strip()]
# Auto-detect Azure hostname
if 'WEBSITE_HOSTNAME' in os.environ:
    ALLOWED_HOSTS.append(os.environ['WEBSITE_HOSTNAME'])

# ── CSRF (critical for Azure HTTPS) ──
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']
_env_origins = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if _env_origins:
    CSRF_TRUSTED_ORIGINS += [o.strip() for o in _env_origins.split(',') if o.strip()]
if 'WEBSITE_HOSTNAME' in os.environ:
    CSRF_TRUSTED_ORIGINS.append(f"https://{os.environ['WEBSITE_HOSTNAME']}")

# ── Apps ──
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'core',
]

# ── Middleware ──
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'deepfakeshield.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'deepfakeshield.wsgi.application'

# ── Database ──
_db_url = os.environ.get('DATABASE_URL', '')
if _db_url:
    DATABASES = {
        'default': dj_database_url.parse(
            _db_url,
            conn_max_age=600,
            ssl_require=os.environ.get('DB_SSL_REQUIRE', 'False').lower() == 'true',
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ── Password Validation ──
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internationalization ──
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ── Static Files (WhiteNoise) ──
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── Media Files ──
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── File Upload Limits ──
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024   # 100MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024


# ═══════════════════════════════════════════════════════════════
# SOLUTION: Emails won't appear in Gmail sent folder
# Use Brevo (free) instead of Gmail SMTP
# Free: 300 emails/day, no Gmail sent folder, professional delivery
# ═══════════════════════════════════════════════════════════════

# STEP 1: Install on VM:
# ~/venv/bin/pip install django-anymail[brevo]

# STEP 2: Get free Brevo API key:
# 1. Go to https://brevo.com → Sign up (free, no credit card)
# 2. Settings → API Keys → Create new key
# 3. Copy the key

# STEP 3: Add to your .env file on VM:
# BREVO_API_KEY=xkeysib-your-key-here

# STEP 4: Add this to settings.py (replaces Gmail email settings):

# Check if Brevo key is available
BREVO_API_KEY = os.environ.get('BREVO_API_KEY', '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')

if BREVO_API_KEY:
    # Use Brevo — emails go directly, NEVER appear in Gmail sent folder
    INSTALLED_APPS += ['anymail']
    EMAIL_BACKEND = 'anymail.backends.brevo.EmailBackend'
    ANYMAIL = {
        'BREVO_API_KEY': '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',
    }
    DEFAULT_FROM_EMAIL = 'DeepFake Shield <deepfakeshield.admin@gmail.com>'
else:
    # Fallback: Gmail SMTP (emails DO appear in sent folder)
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_TIMEOUT = 10
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'deepfakeshield.admin@gmail.com')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'blolqgkyoydxkbbp')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'deepfakeshield.admin@gmail.com')

# ═══════════════════════════════════════════════════════════════
# WHY BREVO IS BETTER FOR THIS:
# - Emails sent via Brevo API — NOT through your Gmail account
# - Zero emails in your Gmail sent folder
# - 300 free emails/day (enough for students/exam demo)
# - Professional email delivery with DeepFake Shield branding
# - Sender shows as "DeepFake Shield <noreply@deepfakeshield.tech>"
# - No Gmail App Password needed
# ═══════════════════════════════════════════════════════════════
# ── Email (Gmail with timeout fix) ──


# ── Site URL (for email verification links) ──
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000')

# ── Security Headers (production only) ──
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'SAMEORIGIN'

# ── Logging ──
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '{levelname} {asctime} {module} {message}', 'style': '{'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
    },
    'root': {'handlers': ['console'], 'level': os.environ.get('LOG_LEVEL', 'INFO')},
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'WARNING', 'propagate': False},
        'core': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'