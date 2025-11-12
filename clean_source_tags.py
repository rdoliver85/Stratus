import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobs.models import Job

print("Cleaning source tags from descriptions...")

jobs = Job.objects.all()
cleaned = 0

for job in jobs:
    # Remove "Source: ... (ID: ...)" lines
    cleaned_desc = re.sub(r'\n\nSource:.*?\(ID:.*?\)', '', job.description)
    
    if cleaned_desc != job.description:
        job.description = cleaned_desc
        job.save()
        cleaned += 1

print(f"Cleaned {cleaned} job descriptions")