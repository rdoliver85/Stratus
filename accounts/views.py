from django_ratelimit.decorators import ratelimit
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile

@never_cache
@ratelimit(key='ip', rate='3/h', method='POST')
def register_view(request):
    # Check if rate limited
    if getattr(request, 'limited', False):
        messages.error(
            request,
            'Too many registration attempts. Please try again later.'
        )
        return render(request, 'accounts/register.html', {'form': UserCreationForm()})
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        is_veteran = request.POST.get('is_veteran') == 'on'
        
        # Validation
        if password1 != password2:
            messages.error(request, "Passwords don't match.")
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'accounts/register.html')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create profile
        UserProfile.objects.create(
            user=user,
            is_veteran=is_veteran
        )
        
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')
    
    return render(request, 'accounts/register.html')
    
@never_cache
@ratelimit(key='ip', rate='5/m', method='POST')
@ratelimit(key='user', rate='5/m', method='POST')
def login_view(request):
    # Check if rate limited
    if getattr(request, 'limited', False):
        messages.error(
            request, 
            'Too many login attempts. Please wait a few minutes and try again.'
        )
        return render(request, 'accounts/login.html', {'form': AuthenticationForm()})
    """User login view"""
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next', 'profile')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, "You've been logged out successfully.")
    return redirect('public_site:homepage')  # Or use '/'

@login_required
def profile_view(request):
    """User profile view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update profile
        profile.is_veteran = request.POST.get('is_veteran') == 'on'
        profile.military_branch = request.POST.get('military_branch', '')
        profile.years_of_service = request.POST.get('years_of_service') or None
        profile.mos_code = request.POST.get('mos_code', '')
        profile.current_clearance = request.POST.get('current_clearance', 'none')
        profile.save()
        
        # Update user info
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')
    
    context = {
        'profile': profile,
        'user': request.user,
    }
    return render(request, 'accounts/profile.html', context)