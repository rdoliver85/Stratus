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