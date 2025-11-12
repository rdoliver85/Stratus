from django.db import models
from companies.models import Company
import uuid

class Job(models.Model):
    job_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)
    responsibilities = models.TextField(blank=True, null=True)
    benefits = models.TextField(blank=True, null=True)
    application_url = models.URLField(max_length=500, blank=True, null=True)
    
    EMPLOYMENT_TYPES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
        ('internship', 'Internship'),
    ]
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default='full_time')
    
    EXPERIENCE_LEVELS = [
        ('entry_level', 'Entry Level'),
        ('mid_level', 'Mid Level'),
        ('senior_level', 'Senior Level'),
        ('executive', 'Executive'),
    ]
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default='mid_level')
    
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    salary_currency = models.CharField(max_length=3, default='USD')
    
    location_city = models.CharField(max_length=100, blank=True)
    location_state = models.CharField(max_length=50, blank=True)
    location_country = models.CharField(max_length=50, default='US')
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    is_remote = models.BooleanField(default=False)
    is_hybrid = models.BooleanField(default=False)
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('filled', 'Filled'),
        ('expired', 'Expired'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    views_count = models.IntegerField(default=0)
    applications_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
# VETERAN-SPECIFIC FIELDS
    is_veteran_friendly = models.BooleanField(default=False, help_text="Company supports veteran hiring")
    veteran_preference = models.BooleanField(default=False, help_text="Veterans given hiring preference")
    military_spouse_preference = models.BooleanField(default=False)
    
    CLEARANCE_LEVELS = [
        ('none', 'No Clearance Required'),
        ('confidential', 'Confidential'),
        ('secret', 'Secret'),
        ('top_secret', 'Top Secret'),
        ('ts_sci', 'TS/SCI'),
    ]
    security_clearance = models.CharField(max_length=20, choices=CLEARANCE_LEVELS, default='none', blank=True)
    
# Military Occupational Specialty (MOS) codes that match this job
    applicable_mos_codes = models.TextField(blank=True, help_text="Comma-separated MOS codes")
    
# Military skills translation
    military_skills_valued = models.TextField(blank=True, help_text="Military skills applicable: leadership, logistics, technical, etc.")
    
# Veteran benefits
    veteran_benefits = models.TextField(blank=True, help_text="GI Bill support, transition assistance, etc.")
    offers_transition_support = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'jobs'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
