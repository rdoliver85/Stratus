from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'industry', 'company_size', 'headquarters_city', 'is_verified']
    list_filter = ['industry', 'company_size', 'is_verified']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}