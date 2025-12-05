from django.contrib import admin
from django.urls import path, include
import os
from dotenv import load_dotenv

load_dotenv()

# Custom admin URL from environment
ADMIN_URL = os.getenv('ADMIN_URL', 'admin/')

# Customize admin site branding
admin.site.site_header = "Stratus Platform Administration"
admin.site.site_title = "Stratus Admin"
admin.site.index_title = "Platform Management"

urlpatterns = [
    path(ADMIN_URL, admin.site.urls),  # Scrambled admin URL
    path('accounts/', include('accounts.urls')),
    path('contact/', include('contact.urls')),
    path('jobs/', include('jobs.urls')),
    path('', include('public_site.urls')),
]