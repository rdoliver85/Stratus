from .settings import *
import os

DEBUG = False

ALLOWED_HOSTS = ['stratusjobs.com', 'www.stratusjobs.com', '.railway.app']

CSRF_TRUSTED_ORIGINS = ['https://stratusjobs.com', 'https://www.stratusjobs.com', 'https://*.railway.app']

# Database from Railway environment
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PGDATABASE'),
        'USER': os.environ.get('PGUSER'),
        'PASSWORD': os.environ.get('PGPASSWORD'),
        'HOST': os.environ.get('PGHOST'),
        'PORT': os.environ.get('PGPORT', 5432),
    }
}

# Security - Railway proxy settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
