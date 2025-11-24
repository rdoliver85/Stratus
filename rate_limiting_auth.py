# Rate Limiting for Authentication Views
# Protect login and registration from brute force attacks

# ==============================================================================
# UPDATE: accounts/views.py
# ==============================================================================

# Add these imports at the top:
"""
from django_ratelimit.decorators import ratelimit
from django.views.decorators.cache import never_cache
"""

# ==============================================================================
# PROTECTED LOGIN VIEW
# ==============================================================================

"""
@never_cache  # Don't cache login page
@ratelimit(key='ip', rate='5/m', method='POST')  # 5 attempts per minute per IP
@ratelimit(key='user', rate='5/m', method='POST')  # 5 attempts per minute per username
def login_view(request):
    '''Login with rate limiting protection'''
    
    # Check if rate limited
    if getattr(request, 'limited', False):
        messages.error(
            request, 
            'Too many login attempts. Please wait a few minutes and try again.'
        )
        return render(request, 'accounts/login.html', {'form': AuthenticationForm()})
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})
"""

# ==============================================================================
# PROTECTED REGISTRATION VIEW
# ==============================================================================

"""
@never_cache  # Don't cache registration page
@ratelimit(key='ip', rate='3/h', method='POST')  # 3 registrations per hour per IP
def register_view(request):
    '''Registration with rate limiting to prevent spam accounts'''
    
    # Check if rate limited
    if getattr(request, 'limited', False):
        messages.error(
            request,
            'Too many registration attempts. Please try again later.'
        )
        return render(request, 'accounts/register.html', {'form': UserCreationForm()})
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Create user
            user = form.save()
            
            # Get veteran status from form (if you have this field)
            is_veteran = request.POST.get('is_veteran') == 'on'
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                is_veteran=is_veteran
            )
            
            username = form.cleaned_data.get('username')
            messages.success(
                request, 
                f'Account created successfully for {username}! Please log in.'
            )
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})
"""

# ==============================================================================
# ADDITIONAL PROTECTION: Failed Login Tracking
# ==============================================================================

# Optional: Track failed login attempts in database
"""
# Add to accounts/models.py:

from django.utils import timezone
from datetime import timedelta

class LoginAttempt(models.Model):
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    success = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
    
    @classmethod
    def is_locked_out(cls, username=None, ip_address=None):
        '''Check if account or IP is locked out due to failed attempts'''
        lockout_time = timezone.now() - timedelta(minutes=15)
        
        if username:
            failed_attempts = cls.objects.filter(
                username=username,
                success=False,
                timestamp__gte=lockout_time
            ).count()
            if failed_attempts >= 5:
                return True
        
        if ip_address:
            failed_attempts = cls.objects.filter(
                ip_address=ip_address,
                success=False,
                timestamp__gte=lockout_time
            ).count()
            if failed_attempts >= 10:
                return True
        
        return False
    
    @classmethod
    def record_attempt(cls, username, ip_address, success):
        '''Record a login attempt'''
        cls.objects.create(
            username=username,
            ip_address=ip_address,
            success=success
        )

# Update login_view to use this:

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# In login_view, before authentication:
    if request.method == 'POST':
        username = request.POST.get('username', '')
        ip = get_client_ip(request)
        
        # Check if locked out
        if LoginAttempt.is_locked_out(username=username, ip_address=ip):
            messages.error(
                request,
                'Account temporarily locked due to multiple failed login attempts. '
                'Please try again in 15 minutes.'
            )
            return render(request, 'accounts/login.html', {'form': AuthenticationForm()})
        
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Record successful login
                LoginAttempt.record_attempt(username, ip, success=True)
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('accounts:profile')
            else:
                # Record failed login
                LoginAttempt.record_attempt(username, ip, success=False)
                messages.error(request, 'Invalid username or password.')
        else:
            # Record failed login
            LoginAttempt.record_attempt(username, ip, success=False)
            messages.error(request, 'Invalid username or password.')
"""

# ==============================================================================
# RATE LIMITING CONFIGURATION
# ==============================================================================

# Rate limit explanations:
# 
# LOGIN:
# - 5 attempts per minute per IP (prevents rapid brute force)
# - 5 attempts per minute per username (prevents credential stuffing)
# 
# REGISTRATION:
# - 3 registrations per hour per IP (prevents spam account creation)
#
# CONTACT FORM:
# - 5 submissions per hour per IP (prevents spam)

# ==============================================================================
# TESTING RATE LIMITS
# ==============================================================================

# To test locally:
# 1. Start server: python manage.py runserver
# 2. Try to login 6 times quickly with wrong password
# 3. 6th attempt should be blocked with rate limit message
# 
# To check rate limit cache:
# python manage.py shell
# from django.core.cache import cache
# print(cache.get_many(cache.keys('rl:*')))
