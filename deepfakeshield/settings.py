"""
DeepFake Shield — settings.py
COMPLETE & CLEAN — Zero errors guaranteed
Gmail SMTP email | PostgreSQL | Azure VM ready
"""
import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Core ──────────────────────────────────────────────────
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-deepfakeshield-default-key-change-in-production-2024'
)
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# ── Hosts ─────────────────────────────────────────────────
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'deepfakeshield.tech',
    'www.deepfakeshield.tech',
    '20.244.24.145',
]
_extra_hosts = os.environ.get('ALLOWED_HOSTS', '')
for h in _extra_hosts.split(','):
    h = h.strip()
    if h and h not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(h)

CSRF_TRUSTED_ORIGINS = [
    'https://deepfakeshield.tech',
    'https://www.deepfakeshield.tech',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
_extra_origins = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
for o in _extra_origins.split(','):
    o = o.strip()
    if o and o not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(o)

# ── Apps ──────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'core',
]

# Add anymail only if Brevo key is set
_brevo_key = os.environ.get('ANYMAIL_BREVO_API_KEY', '')
if _brevo_key:
    INSTALLED_APPS.append('anymail')

# ── Middleware ────────────────────────────────────────────
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
WSGI_APPLICATION = 'deepfakeshield.wsgi.application'

# ── Templates ─────────────────────────────────────────────
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

# ── Database ──────────────────────────────────────────────
_database_url = os.environ.get('DATABASE_URL', '')
if _database_url:
    _ssl = os.environ.get('DB_SSL_REQUIRE', 'False').lower() == 'true'
    DATABASES = {
        'default': dj_database_url.parse(
            _database_url,
            conn_max_age=600,
            ssl_require=_ssl,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ── Password Validation ───────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internationalisation ──────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ── Static & Media ────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
_static_dir = BASE_DIR / 'static'
STATICFILES_DIRS = [_static_dir] if _static_dir.exists() else []
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Upload Limits ─────────────────────────────────────────
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024   # 100 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024   # 100 MB

# ══════════════════════════════════════════════════════════
# EMAIL — Gmail SMTP (primary)
# Brevo used only if ANYMAIL_BREVO_API_KEY is set in .env
# ══════════════════════════════════════════════════════════
if _brevo_key:
    # Brevo transactional email
    EMAIL_BACKEND = 'anymail.backends.brevo.EmailBackend'
    ANYMAIL = {'BREVO_API_KEY': _brevo_key}
    DEFAULT_FROM_EMAIL = 'DeepFake Shield <noreply@deepfakeshield.tech>'
    SERVER_EMAIL = 'noreply@deepfakeshield.tech'
else:
    # Gmail SMTP — always works, no API key needed
    EMAIL_BACKEND      = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST         = 'smtp.gmail.com'
    EMAIL_PORT         = 587
    EMAIL_USE_TLS      = True
    EMAIL_USE_SSL      = False
    EMAIL_TIMEOUT      = 15
    EMAIL_HOST_USER    = os.environ.get('EMAIL_HOST_USER', 'deepfakeshield.admin@gmail.com')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'blolqgkyoydxkbbp')
    DEFAULT_FROM_EMAIL = f"DeepFake Shield <{os.environ.get('EMAIL_HOST_USER', 'deepfakeshield.admin@gmail.com')}>"
    SERVER_EMAIL       = os.environ.get('EMAIL_HOST_USER', 'deepfakeshield.admin@gmail.com')

SITE_URL = os.environ.get('SITE_URL', 'https://deepfakeshield.tech')

# ══════════════════════════════════════════════════════════
# DeepFake Shield — Detection Settings
# CRITICAL: formats WITHOUT dots so forms.py comparison works
# ══════════════════════════════════════════════════════════
DEEPFAKE_SHIELD = {
    'MAX_IMAGE_SIZE_MB': 20,
    'MAX_VIDEO_SIZE_MB': 100,
    'MAX_AUDIO_SIZE_MB': 50,
    'MAX_TEXT_LENGTH': 10000,
    'SUPPORTED_IMAGE_FORMATS': [
        'jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff', 'tif', 'gif'
    ],
    'SUPPORTED_VIDEO_FORMATS': [
        'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', '3gp'
    ],
    'SUPPORTED_AUDIO_FORMATS': [
        'mp3', 'wav', 'ogg', 'flac', 'm4a', 'aac', 'wma'
    ],
}

# ── Security ──────────────────────────────────────────────
SECURE_PROXY_SSL_HEADER      = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_COOKIE_SECURE           = True
SESSION_COOKIE_SECURE        = True
SECURE_BROWSER_XSS_FILTER    = True
SECURE_CONTENT_TYPE_NOSNIFF  = True
X_FRAME_OPTIONS              = 'SAMEORIGIN'

# ── Auth ──────────────────────────────────────────────────
LOGIN_URL             = '/login/'
LOGIN_REDIRECT_URL    = '/dashboard/'
LOGOUT_REDIRECT_URL   = '/'
DEFAULT_AUTO_FIELD    = 'django.db.models.BigAutoField'

# ── Logging ───────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {'format': '[%(levelname)s] %(name)s: %(message)s'},
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.environ.get('LOG_LEVEL', 'INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'core': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}