import os
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config("SECRET_KEY", default="unsafe-development-key")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "rest_framework_simplejwt.token_blacklist",
    "apps.core",
    "apps.accounts",
    "apps.academics",
    "apps.attendance",
    "apps.fees",
    "apps.exams",
    "apps.notices",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3" if os.environ.get("DJANGO_TESTING") else "django.db.backends.postgresql",
        "NAME": ":memory:" if os.environ.get("DJANGO_TESTING") else config("DB_NAME", default="coaching_db"),
        "USER": config("DB_USER", default="coaching_user"),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="http://localhost:5173", cast=Csv())
GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID", default="")
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default=config("EMAIL_FROM", default=""))
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default=config("EMAIL_PASSWORD", default=""))
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)
EMAIL_TIMEOUT = config("EMAIL_TIMEOUT", default=15, cast=int)
ESEWA_FORM_URL = config("ESEWA_FORM_URL", default=config("ESEWA_GATEWAY_URL", default="https://rc-epay.esewa.com.np/api/epay/main/v2/form"))
ESEWA_PRODUCT_CODE = config("ESEWA_PRODUCT_CODE", default="")
ESEWA_SECRET_KEY = config("ESEWA_SECRET_KEY", default="")
ESEWA_STATUS_URL = config("ESEWA_STATUS_URL", default="https://rc-epay.esewa.com.np/api/epay/transaction/status/")
ESEWA_SUCCESS_URL = config("ESEWA_SUCCESS_URL", default="http://localhost:5173/student/payments/esewa/success")
ESEWA_FAILURE_URL = config("ESEWA_FAILURE_URL", default="http://localhost:5173/student/payments/esewa/failure")

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "config.pagination.StandardPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_THROTTLE_CLASSES": ("rest_framework.throttling.AnonRateThrottle",),
    "DEFAULT_THROTTLE_RATES": {"anon": "100/hour", "user": "1000/hour", "esewa": "30/minute"},
}
SPECTACULAR_SETTINGS = {
    "TITLE": "Coaching Management API",
    "DESCRIPTION": "Role-based, multi-tenant coaching center management API.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
from datetime import timedelta
SIMPLE_JWT = {
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}
