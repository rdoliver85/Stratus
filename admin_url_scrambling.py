# Admin URL Scrambling Implementation
# This moves your admin panel from /admin/ to a custom obscured URL

# ==============================================================================
# STEP 1: Update job_platform/urls.py
# ==============================================================================

# BEFORE (your current setup):
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     ...
# ]

# AFTER (new scrambled admin URL):
# Generate a random admin path. Use this generator or create your own:

import secrets
import string

def generate_admin_path():
    """Generate a random 16-character admin URL"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(16))

# Example generated: 'k8m2x7p4n9q3w6f5'

# ==============================================================================
# RECOMMENDED ADMIN URL STRUCTURE
# ==============================================================================

# Option 1: Completely random (most secure)
# admin_url = 'k8m2x7p4n9q3w6f5/'

# Option 2: Memorable but obscured (balance of security & usability)
# admin_url = 'secure-portal-2847/'

# Option 3: Professional but hidden
# admin_url = 'management-console-xk9/'

# ==============================================================================
# YOUR urls.py SHOULD LOOK LIKE THIS:
# ==============================================================================

"""
from django.contrib import admin
from django.urls import path, include

# Choose your admin URL (one of the options above)
ADMIN_URL = 'secure-portal-2847/'  # CHANGE THIS to your chosen path

urlpatterns = [
    path(ADMIN_URL, admin.site.urls),  # Hidden admin URL
    path('accounts/', include('accounts.urls')),
    path('', include('public_site.urls')),
]
"""

# ==============================================================================
# STEP 2: Update Django Admin Site Branding
# ==============================================================================

# Add this to job_platform/urls.py BEFORE urlpatterns:

"""
# Customize admin site
admin.site.site_header = "Stratus Platform Administration"
admin.site.site_title = "Stratus Admin"
admin.site.index_title = "Platform Management"
"""

# ==============================================================================
# STEP 3: Save Your Admin URL
# ==============================================================================

# CRITICAL: Save your new admin URL in a secure location!
# Add to your .env file (NOT in Git):

# .env file:
# ADMIN_URL=secure-portal-2847/

# Then in urls.py, you can load it from environment:
"""
import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_URL = os.getenv('ADMIN_URL', 'admin/')  # Fallback to default if not set
"""

# ==============================================================================
# STEP 4: Update Bookmarks & Documentation
# ==============================================================================

# Update your saved links:
# OLD: https://stratusjobs.com/admin/
# NEW: https://stratusjobs.com/secure-portal-2847/

# ==============================================================================
# ADDITIONAL PROTECTION: IP WHITELISTING (Optional)
# ==============================================================================

# If you want to restrict admin to specific IPs, create middleware:

"""
# Create: job_platform/middleware/admin_ip_whitelist.py

from django.core.exceptions import PermissionDenied
from django.conf import settings

class AdminIPWhitelistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.whitelist = getattr(settings, 'ADMIN_IP_WHITELIST', [])

    def __call__(self, request):
        if request.path.startswith(f'/{settings.ADMIN_URL}'):
            ip = self.get_client_ip(request)
            if self.whitelist and ip not in self.whitelist:
                raise PermissionDenied("Access denied")
        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

# Add to settings.py:
# MIDDLEWARE = [
#     ...
#     'job_platform.middleware.admin_ip_whitelist.AdminIPWhitelistMiddleware',
# ]
# 
# ADMIN_IP_WHITELIST = [
#     '192.168.1.100',  # Your home IP
#     '10.0.0.1',        # Your office IP
# ]
"""

# ==============================================================================
# TESTING
# ==============================================================================

# After implementation:
# 1. Visit https://stratusjobs.com/admin/ - should return 404
# 2. Visit https://stratusjobs.com/your-new-url/ - should show login
# 3. Check Railway logs for any 404s on /admin/ from bots
