"""
Django settings for myproject project.
"""
import os
from pathlib import Path
from datetime import timedelta
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------- Base ----------
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
DEBUG = os.getenv("DEBUG", "True") == "True"

def _split_env(name, default=""):
    return [x.strip() for x in os.getenv(name, default).split(",") if x.strip()]

ALLOWED_HOSTS = _split_env("ALLOWED_HOSTS", "localhost,127.0.0.1,202.28.49.122")
CSRF_TRUSTED_ORIGINS = _split_env(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000,http://202.28.49.122,http://202.28.49.122:8000,https://202.28.49.122"
)

# ---------- Apps ----------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "myapp.apps.MyappConfig",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ---------- Middleware / Templates / WSGI ----------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "myproject.urls"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ],
    },
}]

WSGI_APPLICATION = "myproject.wsgi.application"

# ---------- Database ----------
# ตัวอย่าง DATABASE_URL: postgres://appuser:apppass@postgres:5432/appdb
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL", "postgres://appuser:apppass@postgres:5432/appdb"),
        conn_max_age=600,
        ssl_require=False,
    )
}

# ---------- Password / I18N ----------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Bangkok"
USE_I18N = True
USE_TZ = True

# ---------- Static / Media ----------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
_static = BASE_DIR / "static"
STATICFILES_DIRS = [_static] if _static.exists() else []
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ---------- Security for production ----------
if not DEBUG:
    SESSION_COOKIE_SECURE = False   # ตั้ง True ถ้าเข้าผ่าน HTTPS แท้
    CSRF_COOKIE_SECURE = False      # ตั้ง True ถ้าเข้าผ่าน HTTPS แท้
    SECURE_HSTS_SECONDS = 0         # เปิด HSTS เฉพาะเมื่อมี HTTPS
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False

# ---------- Email (ตามเดิม) ----------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'isrno.100@gmail.com'
EMAIL_HOST_PASSWORD = 'jljjkcaatennnznn'
