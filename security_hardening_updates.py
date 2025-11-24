# Security Hardening Updates for Stratus Platform
# Add these to your job_platform/production_settings.py

# ==============================================================================
# SECURITY HEADERS
# ==============================================================================

# Prevent clickjacking attacks
X_FRAME_OPTIONS = 'DENY'

# Prevent MIME type sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True

# Enable browser XSS protection
SECURE_BROWSER_XSS_FILTER = True

# Force HTTPS for all requests (already set, but verify)
SECURE_SSL_REDIRECT = True

# HSTS - Tell browsers to only use HTTPS for 1 year
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ==============================================================================
# SESSION SECURITY
# ==============================================================================

# Session cookies only sent over HTTPS
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'  # Prevent CSRF

# Session expires when browser closes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Session timeout - 2 hours of inactivity
SESSION_COOKIE_AGE = 7200  # seconds

# CSRF cookies only sent over HTTPS
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# ==============================================================================
# ADDITIONAL CSRF PROTECTION
# ==============================================================================

# Require CSRF token on all unsafe methods
CSRF_USE_SESSIONS = True

# Trusted origins for CSRF (already set, but verify it's complete)
# CSRF_TRUSTED_ORIGINS should include your domain

# ==============================================================================
# PASSWORD VALIDATION (enhance existing)
# ==============================================================================

# Add to existing AUTH_PASSWORD_VALIDATORS
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Most secure
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# ==============================================================================
# RATE LIMITING CONFIGURATION
# ==============================================================================

# These will be used by django-ratelimit decorators
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'  # Uses default cache

# Cache configuration for rate limiting
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'rate_limit_cache',
    }
}

# ==============================================================================
# ADMIN SECURITY
# ==============================================================================

# Admin session timeout - 30 minutes
ADMIN_SESSION_COOKIE_AGE = 1800

# Require staff/admin status for admin access (Django default, but explicit)
ADMIN_SITE_HEADER = "Stratus Platform Administration"
ADMIN_SITE_TITLE = "Stratus Admin"

# ==============================================================================
# LOGGING FOR SECURITY EVENTS
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/tmp/django_security.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# ==============================================================================
# CONTENT SECURITY POLICY
# ==============================================================================

# Add django-csp to MIDDLEWARE and configure
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "code.jquery.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "fonts.googleapis.com")
CSP_FONT_SRC = ("'self'", "fonts.gstatic.com", "cdn.jsdelivr.net")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)  # Prevent framing

# ==============================================================================
# ADDITIONAL SECURITY SETTINGS
# ==============================================================================

# Prevent host header attacks
ALLOWED_HOSTS = ['stratusjobs.com', 'www.stratusjobs.com', '.railway.app']

# Require referrer for form submissions
SECURE_REFERRER_POLICY = 'same-origin'

# Prevent browsers from guessing content types
SECURE_CONTENT_TYPE_NOSNIFF = True
