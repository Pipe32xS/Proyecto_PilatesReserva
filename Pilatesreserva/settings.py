# Pilatesreserva/settings.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-!7j*@b!3h6e&d@(zu@6+d8ac@+4tr1h#agatv1zv(ar+*&3s9g"
DEBUG = True
ALLOWED_HOSTS = []  # agrega dominios en producción

# ─────────────────────────────
# Apps
# ─────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Terceros
    "crispy_forms",

    # Apps del proyecto
    "administrador",
    "usuarios",
    "index",
    "login",
]

# ─────────────────────────────
# Middleware
# ─────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "Pilatesreserva.urls"

# ─────────────────────────────
# Templates
# ─────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "Pilatesreserva.wsgi.application"

# ─────────────────────────────
# Base de datos
# ─────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ─────────────────────────────
# Password validators
# ─────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ─────────────────────────────
# Localización
# ─────────────────────────────
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

# ─────────────────────────────
# Archivos estáticos
# ─────────────────────────────
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─────────────────────────────
# Usuario personalizado
# ─────────────────────────────
AUTH_USER_MODEL = "login.User"

# ─────────────────────────────
# Backends de autenticación
# ─────────────────────────────
AUTHENTICATION_BACKENDS = [
    "login.backends.EmailOrUsernameModelBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# ─────────────────────────────
# Login / Logout redirects
# ─────────────────────────────
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "usuarios:home_cliente"
LOGOUT_REDIRECT_URL = "index:index"

# ─────────────────────────────
# Crispy Forms
# ─────────────────────────────
CRISPY_TEMPLATE_PACK = "bootstrap4"

# ─────────────────────────────
# Email (Reset password)
# ─────────────────────────────

# 🔹 En desarrollo: manda los emails a la consola
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# 🔹 Opción 1: Gmail (requiere App Password de Google)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "tu_correo@gmail.com"         # 👉 reemplazar
EMAIL_HOST_PASSWORD = "TU_APP_PASSWORD"         # 👉 contraseña de aplicación
DEFAULT_FROM_EMAIL = "PilatesReserva <tu_correo@gmail.com>"

# 🔹 Opción 2: Outlook/Office 365 (comentando Gmail arriba y activando este bloque)
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "smtp.office365.com"
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = "tu_correo@outlook.com"     # 👉 reemplazar
# EMAIL_HOST_PASSWORD = "TU_PASSWORD"           # 👉 contraseña (o App Password)
# DEFAULT_FROM_EMAIL = "PilatesReserva <tu_correo@outlook.com>"

# Timeout para conexión SMTP
EMAIL_TIMEOUT = 30

# Link de reseteo válido por 24 horas
PASSWORD_RESET_TIMEOUT = 60 * 60 * 24
