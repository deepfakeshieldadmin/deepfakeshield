"""
DeepFake Shield — settings.py (COMPLETE — Brevo + Gmail fallback)
"""
import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
for h in os.environ.get('ALLOWED_HOSTS', '').split(','):
    if h.strip(): ALLOWED_HOSTS.append(h.strip())
if 'WEBSITE_HOSTNAME' in os.environ:
    ALLOWED_HOSTS.append(os.environ['WEBSITE_HOSTNAME'])

CSRF_TRUSTED_ORIGINS = ['http://localhost:8000']
for o in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(','):
    if o.strip(): CSRF_TRUSTED_ORIGINS.append(o.strip())
if 'WEBSITE_HOSTNAME' in os.environ:
    CSRF_TRUSTED_ORIGINS.append(f"https://{os.environ['WEBSITE_HOSTNAME']}")

# Check for Brevo key (try env first, then hardcoded new key)
_brevo_key = os.environ.get('ANYMAIL_BREVO_API_KEY',
    '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')

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
    'anymail',  # Always include since key is hardcoded
]

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

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

_db = os.environ.get('DATABASE_URL', '')
DATABASES = {
    'default': dj_database_url.parse(_db, conn_max_age=600,
        ssl_require=os.environ.get('DB_SSL_REQUIRE','False').lower()=='true')
} if _db else {
    'default': {'ENGINE':'django.db.backends.sqlite3','NAME': BASE_DIR/'db.sqlite3'}
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024

# ══════════════════════════════════════════════════
# EMAIL — Brevo primary, Gmail SMTP fallback
# ══════════════════════════════════════════════════
EMAIL_BACKEND = 'anymail.backends.brevo.EmailBackend'
ANYMAIL = {
    'BREVO_API_KEY': _brevo_key,
}
DEFAULT_FROM_EMAIL = 'DeepFake Shield <deepfakeshield.admin@gmail.com>'
SERVER_EMAIL = 'deepfakeshield.admin@gmail.com'

# Gmail SMTP fallback settings (used if Brevo fails)
GMAIL_EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', 'deepfakeshield.admin@gmail.com')
GMAIL_EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'blolqgkyoydxkbbp')

SITE_URL = os.environ.get('SITE_URL', 'https://deepfakeshield.tech')

# ══════════════════════════════════════════════════
# DeepFake Shield App Settings
# ══════════════════════════════════════════════════
DEEPFAKE_SHIELD = {
    'MAX_IMAGE_SIZE_MB': 20,
    'MAX_VIDEO_SIZE_MB': 100,
    'MAX_AUDIO_SIZE_MB': 50,
    'MAX_TEXT_LENGTH': 10000,
    'SUPPORTED_IMAGE_FORMATS': ['jpg','jpeg','png','webp','bmp','tiff','tif','gif'],
    'SUPPORTED_VIDEO_FORMATS': ['mp4','avi','mov','mkv','webm','flv','3gp'],
    'SUPPORTED_AUDIO_FORMATS': ['mp3','wav','ogg','flac','m4a','aac','wma'],
}

SECURE_PROXY_SSL_HEADER     = ('HTTP_X_FORWARDED_PROTO','https')
CSRF_COOKIE_SECURE          = SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER   = SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS             = 'SAMEORIGIN'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version':1,'disable_existing_loggers':False,
    'handlers':{'console':{'class':'logging.StreamHandler'}},
    'root':{'handlers':['console'],'level':os.environ.get('LOG_LEVEL','INFO')},
    'loggers':{
        'django':{'handlers':['console'],'level':'WARNING','propagate':False},
        'core':  {'handlers':['console'],'level':'INFO',   'propagate':False},
    },
}