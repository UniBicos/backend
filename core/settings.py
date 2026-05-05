import os
import sys
from pathlib import Path
from datetime import timedelta
import environ

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent

# ========================
# SEGURANÇA
# ========================
SECRET_KEY = env("SECRET_KEY", default="dev-secret-key")

DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))

# ========================
# APPS
# ========================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    # terceiros
    "rest_framework",
    "drf_spectacular",
    # app
    "unibicos.apps.UnibicosConfig",
]

# ========================
# MIDDLEWARE
# ========================
MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "core.urls"

# ========================
# TEMPLATES
# ========================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# ========================
# DATABASE
# =======================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8081",
    "http://127.0.0.1:8081",
]
# ========================
# PASSWORD VALIDATION
# ========================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ========================
# INTERNACIONALIZAÇÃO
# ========================
LANGUAGE_CODE = "pt-br"

TIME_ZONE = "America/Maceio"

USE_I18N = True
USE_TZ = True

# ========================
# STATIC & MEDIA
# ========================
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# ========================
# DJANGO REST FRAMEWORK
# ========================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# ========================
# JWT
# ========================
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ========================
# SWAGGER
# ========================
SPECTACULAR_SETTINGS = {
    "TITLE": "UniBicos API",
    "DESCRIPTION": "API para o marketplace universitário UniBicos",
    "VERSION": "1.0.0",
    # 👇 ESSENCIAL
    "SERVE_INCLUDE_SCHEMA": False,
}


STATIC_URL = "static/"

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

AUTH_USER_MODEL = "unibicos.Usuario"
