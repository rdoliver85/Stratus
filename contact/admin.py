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