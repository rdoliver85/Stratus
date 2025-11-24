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