"""
Django settings for omimi project.

Generated by 'django-admin startproject' using Django 3.2.12.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

import environ

env = environ.Env()

# Read the .env file from the BASE_DIR
environ.Env.read_env(env_file=os.path.join(BASE_DIR, '.env'))





# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-91!8xc543hj37*md&s1*wgfr+p)l+ow=n7bgu4ci5pi#)sz*qc')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=True)

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587  # Use 465 for SSL/TLS encryption
EMAIL_USE_TLS = True  # Use False for SSL/TLS encryption
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')

ALLOWED_HOSTS = ['*']

# CSRF Trusted Origins for Railway deployment
CSRF_TRUSTED_ORIGINS = [
    'https://dadswebsite-production.up.railway.app',
    'https://*.up.railway.app',  # Allows any Railway subdomain
    'https://*.railway.app',     # Additional Railway domains
    'http://127.0.0.1:8000',     # Local development
    'http://localhost:8000',     # Local development alternative
]

# Application definition

INSTALLED_APPS = [
    'projects.apps.ProjectsConfig',
    'django_ckeditor_5',
    'ckeditor',
    'storages',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
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

ROOT_URLCONF = 'omimi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
] 

WSGI_APPLICATION = 'omimi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

import dj_database_url

# Database configuration - Railway automatically provides DATABASE_URL
DATABASE_URL = env('DATABASE_URL', default=None)

if DATABASE_URL:
    # Production database (Railway PostgreSQL)
    print(f"Using PostgreSQL database from DATABASE_URL")
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Local development fallback
    print("Using SQLite database for local development")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Print database engine being used for debugging
print(f"Database engine: {DATABASES['default']['ENGINE']}")

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

# Set to your local timezone - this prevents date confusion in admin
# Change this to your actual timezone (e.g., 'America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles')
TIME_ZONE = 'America/Chicago'  # Central Time - adjust as needed

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
# MEDIA_URL will be automatically set by S3 storage backend when using signed URLs
# MEDIA_URL = '/media/'  # Commented out - S3 storage handles this

# MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')  # Not needed for S3 storage

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),
#'/var/www/static/',
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

customColorPalette = [
    {
        'color': 'hsl(4, 90%, 58%)',
        'label': 'Red'
    },
    {
        'color': 'hsl(340, 82%, 52%)',
        'label': 'Pink'
    },
    {
        'color': 'hsl(291, 64%, 42%)',
        'label': 'Purple'
    },
    {
        'color': 'hsl(262, 52%, 47%)',
        'label': 'Deep Purple'
    },
    {
        'color': 'hsl(231, 48%, 48%)',
        'label': 'Indigo'
    },
    {
        'color': 'hsl(207, 90%, 54%)',
        'label': 'Blue'
    },
]

# CKEDITOR_5_CUSTOM_CSS = 'path_to.css' # optional
# CKEDITOR_5_FILE_STORAGE = "path_to_storage.CustomStorage" # optional
CKEDITOR_5_CONFIGS = {
'default': {
    'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],

    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
        'code','subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                    'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', 'imageUpload', '|',
                    'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                    'insertTable',],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]

        },
        'table': {
            'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
            'tableProperties', 'tableCellProperties' ],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading' : {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        }
    },
    'list': {
        'properties': {
            'styles': 'true',
            'startIndex': 'true',
            'reversed': 'true',
        }
    }
}






# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# AWS S3 Settings - ENABLED FOR S3 INTEGRATION
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default=None)
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default=None)
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default=None)
AWS_S3_REGION_NAME = env('AWS_S3_REGION', default='us-east-1')
# Modern S3 buckets use bucket policies instead of ACLs
AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# S3 Media Settings - ENABLED with signed URLs for private bucket
USE_S3 = env.bool('USE_S3', default=True)

if USE_S3 and AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME:
    # Use custom storage backend for media files
    DEFAULT_FILE_STORAGE = 'projects.storage_backends.MediaStorage'
    AWS_QUERYSTRING_AUTH = True  # Enable signed URLs for private bucket access
    AWS_QUERYSTRING_EXPIRE = 3600  # URLs expire after 1 hour
    AWS_LOCATION = env('AWS_LOCATION', default='media')  # Store media files in 'media' folder
else:
    # Use local file storage for development
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
# S3 URL Configuration for cross-platform compatibility
AWS_S3_SIGNATURE_VERSION = 's3v4'    # Use signature version 4 (more secure)
AWS_S3_ADDRESSING_STYLE = 'virtual'  # Use virtual-hosted style URLs which work better cross-platform
AWS_S3_USE_SSL = True                # Ensure SSL is used for security

# AWS S3 Endpoint URL - enabled for cross-platform compatibility
AWS_S3_ENDPOINT_URL = 'https://s3.amazonaws.com'

# For private buckets, don't set MEDIA_URL - let Django generate signed URLs
# MEDIA_URL will be generated automatically by the storage backend

# Configure static files storage based on S3 availability
if USE_S3 and AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME:
    # Use custom storage backend for static files
    STATICFILES_STORAGE = 'projects.storage_backends.StaticStorage'
    # Override STATIC_URL to point directly to S3 static folder
    STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/static/'
else:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    STATIC_URL = '/static/'

# DynamoDB Settings for Blog Posts
DYNAMODB_BLOG_TABLE = env('DYNAMODB_BLOG_TABLE', default='omimi-blog-posts')

# Caching Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutes
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'aws_blog.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'projects.aws_blog_service': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'projects.aws_views': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Create logs directory if it doesn't exist
import os
LOGS_DIR = BASE_DIR / 'logs'
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
