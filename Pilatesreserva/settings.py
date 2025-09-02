"""
Django settings for Pilatesreserva project.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-!7j*@b!3h6e&d@(zu@6+d8ac@+4tr1h#agatv1zv(ar+*&3s9g'
DEBUG = True
ALLOWED_HOSTS = ['pilatesreserva.onrender.com',
                 'localhost',
                 '127.0.0.1',]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps del proyecto
    'administrador',
    'usuarios',
    'index',
    'login',

    'crispy_forms',
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

ROOT_URLCONF = 'Pilatesreserva.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

WSGI_APPLICATION = 'Pilatesreserva.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'pilatesreserva',
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': (
                'mongodb+srv://felipevallade3_db_user:L9dvNHaTqf7mrO1p'
                '@cluster0.je4jgtc.mongodb.net/pilatesreserva'
                '?retryWrites=true&w=majority&appName=Cluster0'
            ),
        }
    }
}

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

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# <- Tu modelo de usuario personalizado
AUTH_USER_MODEL = 'login.User'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Backends: permite login por email o usuario
AUTHENTICATION_BACKENDS = [
    'login.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# ¡IMPORTANTE! usar el namespace correcto
LOGIN_URL = 'login:login'
LOGIN_REDIRECT_URL = 'usuarios:home_cliente'
LOGOUT_REDIRECT_URL = 'login:login'
