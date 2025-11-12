import os
import django
import requests
from time import sleep

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobs.models import Job

print("\n" + "="*70)
print("JOB URL VALIDATION")
print("="*70)

jobs = Job.objects.filter(status='active')
total = jobs.count()
checked = 0
valid = 0
invalid = 0

for job in jobs:
    checked += 1
    
    if not job.application_url:
        print(f"[{checked}/{total}] ⚠️  No URL: {job.title}")
        job.status = 'expired'
        job.save()
        invalid += 1
        continue
    
    try:
        response = requests.head(job.application_url, timeout=5, allow_redirects=True)
        
        if response.status_code == 200:
            valid += 1
            print(f"[{checked}/{total}] ✓ Valid: {job.title}")
        else:
            invalid += 1
            print(f"[{checked}/{total}] ✗ Invalid ({response.status_code}): {job.title}")
            job.status = 'expired'
            job.save()
    
    except Exception as e:
        invalid += 1
        print(f"[{checked}/{total}] ✗ Error: {job.title}")
        job.status = 'expired'
        job.save()
    
    sleep(0.5)  # Rate limiting

print("\n" + "="*70)
print(f"VALIDATION COMPLETE")
print(f"Total checked: {total}")
print(f"Valid URLs: {valid}")
print(f"Invalid/Expired: {invalid}")
print(f"Active jobs remaining: {Job.objects.filter(status='active').count()}")
print("="*70 + "\n")