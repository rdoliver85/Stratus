import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobs.models import Job

# Keywords that indicate veteran-friendly positions
veteran_keywords = [
    'veteran', 'military', 'clearance', 'security clearance',
    'dod', 'defense', 'federal', 'government', 'usajobs',
    'transition', 'gi bill', 'military spouse'
]

clearance_keywords = {
    'confidential': 'confidential',
    'secret': 'secret',
    'top secret': 'top_secret',
    'ts/sci': 'ts_sci',
    'tssci': 'ts_sci'
}

print("Tagging veteran-friendly jobs...")

updated = 0
for job in Job.objects.all():
    text = (job.title + ' ' + job.description + ' ' + job.company.name).lower()
    
    # Check for veteran-friendly indicators
    if any(keyword in text for keyword in veteran_keywords):
        job.is_veteran_friendly = True
        updated += 1
        
        # Check for veteran preference (government jobs)
        if 'veteran preference' in text or 'usajobs' in text:
            job.veteran_preference = True
        
        # Check for clearance requirements
        for keyword, level in clearance_keywords.items():
            if keyword in text:
                job.security_clearance = level
                break
        
        job.save()
        print(f"✓ Tagged: {job.title}")

print(f"\nTagged {updated} veteran-friendly jobs out of {Job.objects.count()} total")