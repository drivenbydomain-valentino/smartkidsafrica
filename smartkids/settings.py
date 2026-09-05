import os
import tempfile
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# settings.py

# settings.py

AUTH_USER_MODEL = 'club.User'  # Replace 'club' with your exact app_name if different'

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------------
# Core Security & Debug
# -----------------------------------------------------------------------------
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-ym4$awhvr8!si9jfxuya7)g7xk5_fv$r(=ydzmxz_&-2lo=p-&')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'

# Allowed Hosts
ALLOWED_HOSTS = [
    'smartkidsafrica.com',
    'www.smartkidsafrica.com',
    'smartkidsafrica.onrender.com',
    'localhost',
    '127.0.0.1',
    '[::1]',
]
APPEND_SLASH = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

env_hosts = os.environ.get('ALLOWED_HOSTS')
if env_hosts:
    ALLOWED_HOSTS.extend([host.strip() for host in env_hosts.split(',') if host.strip()])

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS = [
    'https://smartkidsafrica.com',
    'https://www.smartkidsafrica.com',
    'http://127.0.0.1:8080',
    'http://localhost:8080',
    'https://*.onrender.com',
]

# Production HTTPS Settings
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# -----------------------------------------------------------------------------
# Application Definition & Middleware
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    # 1. Third-party app overrides
    'whitenoise.runserver_nostatic',
    'cloudinary_storage',

    # 2. Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3. Third-party integrations
    'cloudinary',
    'channels',

    # 4. Local apps
    'club.apps.ClubConfig',
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

ROOT_URLCONF = 'smartkids.urls'
WSGI_APPLICATION = 'smartkids.wsgi.application'
ASGI_APPLICATION = 'smartkids.asgi.application'

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

# -----------------------------------------------------------------------------
# Database Configuration
# -----------------------------------------------------------------------------
# DATABASES = {
#     'default': dj_database_url.config(
#         default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
#         conn_max_age=60,
#         ssl_require=not DEBUG  # Enforces SSL on production Postgres connections
#     )
# }


DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

DATABASE_URL = "https://console.aiven.io/account/a5db89b87a31/project/drivenbydomain-smartkidsafrica/services/pg-a4344c7"

# -----------------------------------------------------------------------------
# Password Validation & Localization
# -----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = 'club:login'
LOGIN_REDIRECT_URL = 'club:home'
# -----------------------------------------------------------------------------
# Static & Media Files (Cloudinary & WhiteNoise)
# -----------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Source static directory for static assets
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'



CLOUDINARY_STORAGE = {
    'SECURE': True,
    'CLOUD_NAME': 'sywzvlna',
    'API_KEY': '862548548812594',
    'API_SECRET': 'lklFKOIkxMjLO_B530_yukmAe70'
}

STORAGES = {
    # Handles media files (user uploads) via Cloudinary
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    # Handles static files (CSS/JS) safely
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Compatibility fallback
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# -----------------------------------------------------------------------------
# Channels & Redis
# -----------------------------------------------------------------------------
REDIS_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379')

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    },
}

# -----------------------------------------------------------------------------
# Upload Limits & Temp Storage
# -----------------------------------------------------------------------------
FILE_UPLOAD_TEMP_DIR = tempfile.gettempdir()
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB

# -----------------------------------------------------------------------------
# Email Configuration
# -----------------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.hostinger.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
EMAIL_HOST_USER = 'mgt@smartkidsafrica.com'
EMAIL_HOST_PASSWORD = 'Sire@1983'
DEFAULT_FROM_EMAIL = 'mgt@smartkidsafrica.com'