from django.db import models
from django.contrib.auth.models import User
import uuid

class UserProfile(models.Model):
    profile_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Veteran status
    is_veteran = models.BooleanField(default=False)
    veteran_verified = models.BooleanField(default=False, help_text="Admin verified veteran status")
    
    MILITARY_BRANCHES = [
        ('army', 'Army'),
        ('navy', 'Navy'),
        ('air_force', 'Air Force'),
        ('marines', 'Marine Corps'),
        ('coast_guard', 'Coast Guard'),
        ('space_force', 'Space Force'),
    ]
    military_branch = models.CharField(max_length=20, choices=MILITARY_BRANCHES, blank=True)
    
    # Service details
    years_of_service = models.IntegerField(null=True, blank=True)
    mos_code = models.CharField(max_length=50, blank=True, help_text="Military Occupational Specialty Code")
    discharge_type = models.CharField(max_length=50, blank=True)
    
    CLEARANCE_LEVELS = [
        ('none', 'No Clearance'),
        ('confidential', 'Confidential'),
        ('secret', 'Secret'),
        ('top_secret', 'Top Secret'),
        ('ts_sci', 'TS/SCI'),
    ]
    current_clearance = models.CharField(max_length=20, choices=CLEARANCE_LEVELS, default='none', blank=True)
    
    # Verification documents (store file path)
    dd214_uploaded = models.BooleanField(default=False, help_text="DD-214 discharge papers uploaded")
    verification_notes = models.TextField(blank=True, help_text="Admin notes on verification")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"{self.user.username} - {'Verified Veteran' if self.veteran_verified else 'User'}"
