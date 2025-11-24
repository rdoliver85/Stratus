from django import forms
from .models import ContactMessage
import re

class ContactForm(forms.ModelForm):
    # Honeypot field (hidden via CSS, bots will fill it)
    honeypot = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'style': 'display:none;',
            'tabindex': '-1',
            'autocomplete': 'off'
        })
    )
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message', 'honeypot']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': True,
                'maxlength': '100'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
                'required': True
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject',
                'required': True,
                'maxlength': '200'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your message...',
                'rows': 6,
                'required': True,
                'maxlength': '2000'
            }),
        }
    
    def clean_honeypot(self):
        '''If honeypot field is filled, it's a bot'''
        honeypot = self.cleaned_data.get('honeypot')
        if honeypot:
            raise forms.ValidationError('Bot detected')
        return honeypot
    
    def clean_email(self):
        '''Validate email format and common spam patterns'''
        email = self.cleaned_data.get('email')
        
        # Block common spam email patterns
        spam_patterns = [
            r'.*@yopmail\.com$',
            r'.*@mailinator\.com$',
            r'.*@guerrillamail\.com$',
            r'.*@10minutemail\.com$',
        ]
        
        for pattern in spam_patterns:
            if re.match(pattern, email, re.IGNORECASE):
                raise forms.ValidationError('Temporary email addresses are not allowed.')
        
        return email
    
    def clean_message(self):
        '''Check for spam patterns in message'''
        message = self.cleaned_data.get('message')
        
        # Block messages with excessive links
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, message)
        
        if len(urls) > 3:
            raise forms.ValidationError('Too many links in message. Please limit to 3 or fewer.')
        
        # Check for common spam phrases
        spam_keywords = ['viagra', 'cialis', 'casino', 'lottery', 'bitcoin mining']
        message_lower = message.lower()
        
        for keyword in spam_keywords:
            if keyword in message_lower:
                raise forms.ValidationError('Message contains prohibited content.')
        
        return message
    
    def clean_name(self):
        '''Validate name field'''
        name = self.cleaned_data.get('name')
        
        # Check for excessive special characters
        if len(re.findall(r'[^a-zA-Z\s\-\']', name)) > 2:
            raise forms.ValidationError('Name contains too many special characters.')
        
        return name