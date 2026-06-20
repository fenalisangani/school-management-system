import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in {'1', 'true', 'yes', 'on'}


def env_list(name, default=''):
    return [item.strip() for item in os.environ.get(name, default).split(',') if item.strip()]


# SECURITY: set SECRET_KEY in the hosting environment for production.
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-change-this-key-in-production',
)

# DEBUG defaults to True for local development. Set DEBUG=False on your host.
DEBUG = env_bool('DEBUG', True)

# Hosts allowed to serve the site. '*' is convenient for local/LAN demos.
# On a real host, set ALLOWED_HOSTS=yourdomain.com (comma separated).
ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', '*')

# Needed for HTTPS form submissions (CSRF) on hosted platforms and tunnels.
# e.g. CSRF_TRUSTED_ORIGINS=https://your-app.onrender.com
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS', '')
# Trust Cloudflare quick-tunnel and common host domains so admin/login forms work
# when shared via a public demo link.
CSRF_TRUSTED_ORIGINS += [
    'https://*.trycloudflare.com',
    'https://*.onrender.com',
    'https://*.ngrok-free.app',
    'https://*.ngrok.io',
]

# Common platforms expose the external hostname via an env var — trust it automatically.
_render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if _render_host:
    ALLOWED_HOSTS.append(_render_host)
    CSRF_TRUSTED_ORIGINS.append(f'https://{_render_host}')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'classes',
    'teachers',
    'students',
    'fees',
    'attendance',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.LoginRequiredMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Authentication redirects (LoginRequiredMiddleware protects every page by default;
# the login view itself is exempted with @login_not_required).
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Enable WhiteNoise (efficient static-file serving for production) only if it's
# installed, so local development works with just Django + Pillow.
try:
    import whitenoise  # noqa: F401

    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    _WHITENOISE_AVAILABLE = True
except ModuleNotFoundError:
    _WHITENOISE_AVAILABLE = False

ROOT_URLCONF = 'core.urls'

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
                'django.template.context_processors.media',
                'core.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database: uses Postgres if DATABASE_URL is provided (persistent on hosts),
# otherwise falls back to local SQLite.
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    import dj_database_url

    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=env_bool('DB_SSL_REQUIRE', True),
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-in'

TIME_ZONE = 'Asia/Kolkata'

# Currency — all fee amounts are stored and displayed in Indian Rupees (INR)
CURRENCY_CODE = 'INR'
CURRENCY_SYMBOL = '₹'
APP_VERSION = '1.0.0'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# WhiteNoise serves static files efficiently in production (no separate web server
# needed). Falls back to Django's default storage when WhiteNoise isn't installed.
if _WHITENOISE_AVAILABLE:
    STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
    }

# Production security hardening (only enforced when DEBUG is False).
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
