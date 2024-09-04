from pathlib import Path
from dotenv import load_dotenv
import os
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-6^^c27_%1u1$%=i=il-6w9hho%%4hxkm=c1e*1(4&3jbw@hzo#"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apis",
    "rest_framework",
    "cloudinary_storage",
    "cloudinary",
    "phonenumber_field",
    "rest_framework_simplejwt",
    "storages",  # Ensure storages is installed for S3 support
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
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
    },
]

WSGI_APPLICATION = "backend.wsgi.application"

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': str(os.getenv("NAME")),
        'USER': str(os.getenv("USER")),
        'PASSWORD': str(os.getenv("PASSWORD")),
        'HOST': str(os.getenv("HOST")),
        'PORT': str(os.getenv("PORT")),
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images) - Local Storage for Static Files
STATICFILES_DIRS = [os.path.join(BASE_DIR, "ui/static")]
STATIC_URL = "ui/staticfiles/"
STATIC_ROOT = os.path.join(BASE_DIR, "ui/staticfiles")
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files - S3 Storage for Media Files
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

AWS_ACCESS_KEY_ID = os.environ.get("SUPABASE_S3_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("SUPABASE_S3_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("SUPABASE_S3_BUCKET_NAME")
AWS_S3_REGION_NAME = os.environ.get("SUPABASE_S3_REGION_NAME")
AWS_S3_ENDPOINT_URL = os.environ.get("SUPABASE_S3_ENDPOINT_URL")
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.supabase.co'

MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/storage/v1/object/public/storage/media/'

# JWT Configuration
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=50000),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=50000),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
}

AUTH_USER_MODEL = 'apis.User'

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': str(os.getenv('CLOUD_NAME')),
    'API_KEY': str(os.getenv('CLOUDINARY_API_KEY')),
    'API_SECRET': str(os.getenv('CLOUDINARY_API_SECRET')),
}

PHONENUMBER_DEFAULT_REGION = 'IN'
