import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobs.models import Job
from collections import defaultdict

print("\n" + "="*70)
print("DUPLICATE JOB REMOVAL")
print("="*70)

# Group jobs by title + company
duplicates = defaultdict(list)

for job in Job.objects.all().select_related('company'):
    key = (job.title.lower().strip(), job.company.name.lower().strip())
    duplicates[key].append(job)

# Find and remove duplicates
total_removed = 0
duplicates_found = 0

for key, job_list in duplicates.items():
    if len(job_list) > 1:
        duplicates_found += 1
        # Keep the newest one, delete the rest
        job_list.sort(key=lambda x: x.created_at, reverse=True)
        keep = job_list[0]
        remove = job_list[1:]
        
        print(f"\nDuplicate: {keep.title} at {keep.company.name}")
        print(f"  Keeping: ID {keep.job_id} (created {keep.created_at})")
        print(f"  Removing: {len(remove)} older copies")
        
        for job in remove:
            job.delete()
            total_removed += 1

print("\n" + "="*70)
print(f"DEDUPLICATION COMPLETE")
print(f"Duplicate groups found: {duplicates_found}")
print(f"Jobs removed: {total_removed}")
print(f"Jobs remaining: {Job.objects.count()}")
print("="*70 + "\n")