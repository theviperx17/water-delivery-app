from pathlib import Path
import os
import dj_database_url  # ✅ ต้องมีบรรทัดนี้
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

SECRET_KEY = "dev-secret-key-change-me"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    # Jazzmin (Admin Theme) - ต้องอยู่ก่อน admin
    'jazzmin',
    
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django.contrib.humanize',
    
    # 3rd-party
    "widget_tweaks",
    
    # Local apps
    "accounts",
    "catalog",
    "orders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ ย้ายมาไว้ตรงนี้ (บรรทัดที่ 2) ดีที่สุดครับ
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "water_d.urls"

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

WSGI_APPLICATION = "water_d.wsgi.application"


# --- Database Configuration (แก้ไขแล้ว) ---
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        # ✅ Config นี้ฉลาดมาก:
        # 1. ถ้าอยู่บน Cloud: มันจะหา Environment Variable ให้อัตโนมัติ
        # 2. ถ้าอยู่ Local: มันจะใช้ค่า default ด้านล่างนี้ (User: postgres / Pass: 1234)
        
        default='postgres://postgres:1234@localhost:5432/water_db',
        conn_max_age=600,
        ssl_require=False
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "th"

TIME_ZONE = "Asia/Bangkok"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

# settings.py (ล่างสุด)
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- Media Files (สำหรับรูปภาพสินค้า) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Login/Logout Redirect
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = 'accounts:dashboard'
LOGOUT_REDIRECT_URL = '/'


# --- JAZZMIN SETTINGS (Admin Theme) ---
JAZZMIN_SETTINGS = {
    "site_title": "Water Delivery Admin",
    "site_header": "Water Delivery",
    "site_brand": "ระบบจัดการส่งน้ำ",
    # "site_logo": "images/logo.png", # ถ้ามีโลโก้ให้เอา comment ออกแล้วใส่ path
    "welcome_sign": "ยินดีต้อนรับสู่ระบบจัดการ Water Delivery",
    "copyright": "Water Delivery Ltd",
    "search_model": "auth.User",
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "accounts.CustomerProfile": "fas fa-user-tag",
        "accounts.Profile": "fas fa-id-card",
        "catalog.Product": "fas fa-bottle-water",
        "orders.Order": "fas fa-clipboard-list",
        "orders.DeliveryRound": "fas fa-truck",
        "orders.DriverLocation": "fas fa-map-marker-alt",
    },
    "order_with_respect_to": ["orders", "catalog", "accounts", "auth"],
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "theme": "flatly",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

# อนุญาตให้ Django ยอมรับลิงก์จาก Ngrok และ Cloud
CSRF_TRUSTED_ORIGINS = [
    'https://fd7d0585e974.ngrok-free.app',  # ลิงก์ Ngrok เดิม
    'https://*.ngrok-free.app',
    'https://*.railway.app',                # ✅ เพิ่มเผื่อไว้สำหรับ Railway
    'https://*.up.railway.app',             # ✅ เพิ่มเผื่อไว้สำหรับ Railway Domain ใหม่
]