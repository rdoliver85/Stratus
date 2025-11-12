import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobs.models import Job
import re

jobs = Job.objects.all()
truncated = []

for job in jobs:
    desc = job.description
    
    # Check for truncation indicators:
    # 1. Ends mid-word (no punctuation at end)
    # 2. Ends with "..." 
    # 3. Very short (under 500 chars is suspicious for a full job description)
    
    is_truncated = False
    reason = ""
    
    if len(desc) < 500:
        is_truncated = True
        reason = f"Too short ({len(desc)} chars)"
    elif desc.endswith('...'):
        is_truncated = True
        reason = "Ends with ..."
    elif not desc[-1] in '.!?)"\n ':  # Doesn't end with proper punctuation
        is_truncated = True
        reason = f"Ends mid-word: '{desc[-50:]}'"
    
    if is_truncated:
        truncated.append({
            'id': job.job_id,
            'title': job.title,
            'company': job.company.name,
            'length': len(desc),
            'reason': reason,
            'url': job.application_url
        })

print(f"\n{'='*70}")
print(f"TRUNCATION ANALYSIS")
print(f"{'='*70}")
print(f"Total jobs: {jobs.count()}")
print(f"Truncated jobs: {len(truncated)}")
print(f"Percentage: {len(truncated)/jobs.count()*100:.1f}%")
print(f"{'='*70}\n")

if truncated:
    print("TRUNCATED JOBS:")
    for i, job in enumerate(truncated[:10], 1):  # Show first 10
        print(f"\n{i}. {job['title']} - {job['company']}")
        print(f"   Length: {job['length']} chars")
        print(f"   Reason: {job['reason']}")
        print(f"   URL: {job['url'][:60]}..." if len(job['url']) > 60 else f"   URL: {job['url']}")
    
    if len(truncated) > 10:
        print(f"\n... and {len(truncated) - 10} more")