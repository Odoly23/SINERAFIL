"""
Django settings ba SINERAFIL - Sistema Informasaun Jestaun Inventáriu Pesa-Rezerva no Reparasaun (Ofisina Nerafil).

Variabel sensitif dibaca husi file .env uza python-decouple (haree .env.example).
"""
from pathlib import Path

from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# ══════════════════════════════════════════════════════════════
#  CORE
# ══════════════════════════════════════════════════════════════
SECRET_KEY = config('SECRET_KEY', default='django-insecure-sinerafil-troka-molok-produsaun')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv())

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third party
    'crispy_forms',
    'crispy_bootstrap4',
    # apps
    'config',
    'custom',
    'main',
    'users',
    'pesa',
    'cliente',
    'servisu',
    'report',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Sinerafil.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main.context_processors.sinerafil',
            ],
        },
    },
]

WSGI_APPLICATION = 'Sinerafil.wsgi.application'

# ══════════════════════════════════════════════════════════════
#  DATABASE (SQLite)
# ══════════════════════════════════════════════════════════════
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 6}},
]

# ══════════════════════════════════════════════════════════════
#  I18N
# ══════════════════════════════════════════════════════════════
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dili'
USE_I18N = False
USE_TZ = True

# ══════════════════════════════════════════════════════════════
#  STATIC & MEDIA
# ══════════════════════════════════════════════════════════════
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ══════════════════════════════════════════════════════════════
#  CRISPY FORMS
# ══════════════════════════════════════════════════════════════
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap4'
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# ══════════════════════════════════════════════════════════════
#  AUTH & LOGIN
# ══════════════════════════════════════════════════════════════
LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login'

# ══════════════════════════════════════════════════════════════
#  IDENTIDADE OFISINA (kop relatóriu PDF no nota)
# ══════════════════════════════════════════════════════════════
SHOP_NAME = config('SHOP_NAME', default='Ofisina Nerafil')
SHOP_TAGLINE = config('SHOP_TAGLINE', default='Reparasaun & Manutensaun Motór')
SHOP_ADDRESS = config('SHOP_ADDRESS', default='Dili, Timor-Leste')
SHOP_PHONE = config('SHOP_PHONE', default='+670 7777 0000')

# Kursu Rupiah per 1 USD (uza de'it bainhira importa Excel)
KURS_RUPIAH_PER_USD = config('KURS_RUPIAH_PER_USD', default=16000, cast=int)
