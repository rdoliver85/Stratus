# Secure Contact Page Implementation for Stratus Platform
# Complete contact form with all security protections

# ==============================================================================
# STEP 1: Create Contact App
# ==============================================================================

# Run in PowerShell:
# cd C:\JobPlatform
# .\venv\Scripts\Activate.ps1
# python manage.py startapp contact

# ==============================================================================
# STEP 2: contact/models.py
# ==============================================================================

"""
from django.db import models
from django.utils import timezone

class ContactMessage(models.Model):
    # Message details
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField(max_length=2000)
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    
    # Status tracking
    is_read = models.BooleanField(default=False)
    is_spam = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)
    
    # Honeypot field (hidden from users, catches bots)
    honeypot = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
    
    def __str__(self):
        return f"{self.name} - {self.subject[:50]}"
    
    def mark_as_spam(self):
        self.is_spam = True
        self.save()
    
    def mark_as_read(self):
        self.is_read = True
        self.save()
"""

# ==============================================================================
# STEP 3: contact/forms.py
# ==============================================================================

"""
from django import forms
from .models import ContactMessage
import re

class ContactForm(forms.ModelForm):
    # Honeypot field (hidden via CSS, bots will fill it)
    honeypot = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'style': 'display:none;',
            'tabindex': '-1',
            'autocomplete': 'off'
        })
    )
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message', 'honeypot']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': True,
                'maxlength': '100'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
                'required': True
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject',
                'required': True,
                'maxlength': '200'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your message...',
                'rows': 6,
                'required': True,
                'maxlength': '2000'
            }),
        }
    
    def clean_honeypot(self):
        '''If honeypot field is filled, it's a bot'''
        honeypot = self.cleaned_data.get('honeypot')
        if honeypot:
            raise forms.ValidationError('Bot detected')
        return honeypot
    
    def clean_email(self):
        '''Validate email format and common spam patterns'''
        email = self.cleaned_data.get('email')
        
        # Block common spam email patterns
        spam_patterns = [
            r'.*@yopmail\.com$',
            r'.*@mailinator\.com$',
            r'.*@guerrillamail\.com$',
            r'.*@10minutemail\.com$',
        ]
        
        for pattern in spam_patterns:
            if re.match(pattern, email, re.IGNORECASE):
                raise forms.ValidationError('Temporary email addresses are not allowed.')
        
        return email
    
    def clean_message(self):
        '''Check for spam patterns in message'''
        message = self.cleaned_data.get('message')
        
        # Block messages with excessive links
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, message)
        
        if len(urls) > 3:
            raise forms.ValidationError('Too many links in message. Please limit to 3 or fewer.')
        
        # Check for common spam phrases
        spam_keywords = ['viagra', 'cialis', 'casino', 'lottery', 'bitcoin mining']
        message_lower = message.lower()
        
        for keyword in spam_keywords:
            if keyword in message_lower:
                raise forms.ValidationError('Message contains prohibited content.')
        
        return message
    
    def clean_name(self):
        '''Validate name field'''
        name = self.cleaned_data.get('name')
        
        # Check for excessive special characters
        if len(re.findall(r'[^a-zA-Z\s\-\']', name)) > 2:
            raise forms.ValidationError('Name contains too many special characters.')
        
        return name
"""

# ==============================================================================
# STEP 4: contact/views.py (with rate limiting)
# ==============================================================================

"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit
from .forms import ContactForm
from .models import ContactMessage

def get_client_ip(request):
    '''Get real IP address even behind proxy'''
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@require_http_methods(["GET", "POST"])
@ratelimit(key='ip', rate='5/h', method='POST')  # 5 submissions per hour per IP
def contact_view(request):
    '''Secure contact form with rate limiting and spam protection'''
    
    # Check if rate limited
    if getattr(request, 'limited', False):
        messages.error(request, 'Too many contact attempts. Please try again later.')
        return render(request, 'contact/contact.html', {'form': ContactForm()})
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        
        if form.is_valid():
            # Don't save yet, add metadata first
            contact_message = form.save(commit=False)
            
            # Add IP address and user agent
            contact_message.ip_address = get_client_ip(request)
            contact_message.user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
            
            # Check honeypot (should be empty)
            if contact_message.honeypot:
                contact_message.is_spam = True
            
            # Save message
            contact_message.save()
            
            # Success message
            if not contact_message.is_spam:
                messages.success(
                    request, 
                    'Thank you for contacting us! We will respond within 24-48 hours.'
                )
            else:
                # Fake success for bots (don't let them know they're caught)
                messages.success(request, 'Thank you for your message.')
            
            return redirect('contact:contact')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    
    return render(request, 'contact/contact.html', {'form': form})
"""

# ==============================================================================
# STEP 5: contact/admin.py
# ==============================================================================

"""
from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_read', 'is_spam']
    list_filter = ['is_read', 'is_spam', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'ip_address', 'user_agent', 'honeypot']
    
    fieldsets = (
        ('Message Details', {
            'fields': ('name', 'email', 'subject', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'is_spam', 'admin_notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'ip_address', 'user_agent', 'honeypot'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_spam', 'mark_as_not_spam']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f'{queryset.count()} messages marked as read.')
    mark_as_read.short_description = 'Mark selected as read'
    
    def mark_as_spam(self, request, queryset):
        queryset.update(is_spam=True)
        self.message_user(request, f'{queryset.count()} messages marked as spam.')
    mark_as_spam.short_description = 'Mark selected as spam'
    
    def mark_as_not_spam(self, request, queryset):
        queryset.update(is_spam=False)
        self.message_user(request, f'{queryset.count()} messages marked as not spam.')
    mark_as_not_spam.short_description = 'Mark selected as not spam'
"""

# ==============================================================================
# STEP 6: contact/urls.py
# ==============================================================================

"""
from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    path('', views.contact_view, name='contact'),
]
"""

# ==============================================================================
# STEP 7: templates/contact/contact.html
# ==============================================================================

"""
{% extends 'base.html' %}

{% block title %}Contact Us - Stratus Jobs{% endblock %}

{% block content %}
<div class="container mt-5 mb-5">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <h1 class="mb-4">Contact Us</h1>
            
            <p class="lead">
                Have a question or need support? Send us a message and we'll get back to you within 24-48 hours.
            </p>
            
            {% if messages %}
                {% for message in messages %}
                    <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
            
            <div class="card shadow-sm">
                <div class="card-body">
                    <form method="post" novalidate>
                        {% csrf_token %}
                        
                        <div class="mb-3">
                            <label for="{{ form.name.id_for_label }}" class="form-label">Name *</label>
                            {{ form.name }}
                            {% if form.name.errors %}
                                <div class="invalid-feedback d-block">
                                    {{ form.name.errors }}
                                </div>
                            {% endif %}
                        </div>
                        
                        <div class="mb-3">
                            <label for="{{ form.email.id_for_label }}" class="form-label">Email Address *</label>
                            {{ form.email }}
                            {% if form.email.errors %}
                                <div class="invalid-feedback d-block">
                                    {{ form.email.errors }}
                                </div>
                            {% endif %}
                        </div>
                        
                        <div class="mb-3">
                            <label for="{{ form.subject.id_for_label }}" class="form-label">Subject *</label>
                            {{ form.subject }}
                            {% if form.subject.errors %}
                                <div class="invalid-feedback d-block">
                                    {{ form.subject.errors }}
                                </div>
                            {% endif %}
                        </div>
                        
                        <div class="mb-3">
                            <label for="{{ form.message.id_for_label }}" class="form-label">Message *</label>
                            {{ form.message }}
                            {% if form.message.errors %}
                                <div class="invalid-feedback d-block">
                                    {{ form.message.errors }}
                                </div>
                            {% endif %}
                        </div>
                        
                        <!-- Honeypot field (hidden from users) -->
                        {{ form.honeypot }}
                        
                        <button type="submit" class="btn btn-primary">Send Message</button>
                    </form>
                </div>
            </div>
            
            <div class="mt-4">
                <h3>Other Ways to Reach Us</h3>
                <p>
                    <strong>For urgent issues:</strong> Please email us directly at 
                    <a href="mailto:support@stratusjobs.com">support@stratusjobs.com</a>
                </p>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# ==============================================================================
# STEP 8: Add to settings.py INSTALLED_APPS
# ==============================================================================

"""
INSTALLED_APPS = [
    ...
    'contact',
]
"""

# ==============================================================================
# STEP 9: Add to main urls.py
# ==============================================================================

"""
urlpatterns = [
    ...
    path('contact/', include('contact.urls')),
]
"""

# ==============================================================================
# STEP 10: Create migrations and apply
# ==============================================================================

# Run in PowerShell:
# python manage.py makemigrations contact
# python manage.py migrate
#
# For Railway (manual migration):
# $env:PGHOST="turntable.proxy.rlwy.net"
# $env:PGPORT="26138"
# $env:PGUSER="postgres"
# $env:PGPASSWORD="<your-password>"
# $env:PGDATABASE="railway"
# $env:DJANGO_SETTINGS_MODULE="job_platform.production_settings"
# python manage.py migrate --settings=job_platform.production_settings
