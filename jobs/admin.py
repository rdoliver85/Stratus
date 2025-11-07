from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location_city', 'employment_type', 'is_veteran_friendly', 'veteran_preference', 'status', 'created_at']
    list_filter = ['employment_type', 'experience_level', 'status', 'is_remote', 'is_veteran_friendly', 'veteran_preference', 'security_clearance']
    search_fields = ['title', 'description', 'location_city', 'military_skills_valued']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'company', 'description', 'requirements', 'responsibilities', 'benefits')
        }),
        ('Employment Details', {
            'fields': ('employment_type', 'experience_level', 'salary_min', 'salary_max', 'status')
        }),
        ('Location', {
            'fields': ('location_city', 'location_state', 'location_country', 'is_remote', 'is_hybrid')
        }),
        ('Veteran-Specific', {
            'fields': ('is_veteran_friendly', 'veteran_preference', 'military_spouse_preference', 
                      'security_clearance', 'applicable_mos_codes', 'military_skills_valued', 
                      'veteran_benefits', 'offers_transition_support'),
            'classes': ('collapse',),  # Collapsible section
        }),
    )