from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location_city', 'employment_type', 'status', 'created_at']
    list_filter = ['employment_type', 'experience_level', 'status', 'is_remote']
    search_fields = ['title', 'description', 'location_city']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-created_at']