"""Local development settings."""

from .base import *

SECRET_KEY = 'django-insecure-tr(d7-z(sahr%kd@iihwqzy^*&-k2c&=-ipmq$auo&8wstgqej'

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' 