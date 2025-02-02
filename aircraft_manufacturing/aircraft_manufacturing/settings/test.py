
from .local import *

TESTING = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

SKIP_INITIAL_DATA = True
