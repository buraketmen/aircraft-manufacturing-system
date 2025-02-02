from pathlib import Path
import os, sys
import logging
import logging.config

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS = True

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.contenttypes',
    
    'rest_framework',
    'corsheaders',
    'drf_yasg',
    'django_filters',
    
    'management',
    'accounts',
    'inventory',
    'assembly',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'aircraft_manufacturing.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'frontend', 'templates')],
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

WSGI_APPLICATION = 'aircraft_manufacturing.wsgi.application'

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

STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'frontend', 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'frontend', 'static'),
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication settings
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": "10/min",
        "user": "120/min",
    },
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1"],
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "UNICODE_JSON": False,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}


SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': None,
    'SERVE_AUTHENTICATION': None,
} 

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standardized": {
            "format": "[%(levelname)s] [%(asctime)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "gunicorn": {
            "format": "[%(levelname)s] [%(asctime)s] [%(name)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            'stream': sys.stdout,
            "formatter": "standardized",
        },
        "gunicorn": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "gunicorn",
            "stream": sys.stdout,
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "gunicorn": {
            "handlers": ["gunicorn"],
            "level": "INFO",
            "propagate": True,
        },
        
        "django.request": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
logging.config.dictConfig(LOGGING)

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True