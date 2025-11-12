import os
import django

# PHASE 1: Export from LOCAL database
print("=" * 60)
print("PHASE 1: EXPORTING FROM LOCAL DATABASE")
print("=" * 60)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.core import serializers
from companies.models import Company
from jobs.models import Job

print("\n[1/2] Exporting companies from local...")
with open('companies_export.json', 'w', encoding='utf-8') as f:
    serializers.serialize('json', Company.objects.all(), indent=2, stream=f, ensure_ascii=False)
print(f"    ✓ Exported {Company.objects.count()} companies")

print("\n[2/2] Exporting jobs from local...")
with open('jobs_export.json', 'w', encoding='utf-8') as f:
    serializers.serialize('json', Job.objects.all(), indent=2, stream=f, ensure_ascii=False)
print(f"    ✓ Exported {Job.objects.count()} jobs")

# PHASE 2: Import to RAILWAY database
print("\n" + "=" * 60)
print("PHASE 2: IMPORTING TO RAILWAY DATABASE")
print("=" * 60)

# Reconnect to Railway
from django.apps import apps
apps.app_configs = {}
apps.all_models = {}
apps.ready = False

os.environ['DJANGO_SETTINGS_MODULE'] = 'job_platform.production_settings'
django.setup()

from django.core.management import call_command

print("\n[1/2] Importing companies to Railway...")
call_command('loaddata', 'companies_export.json', verbosity=1)

print("\n[2/2] Importing jobs to Railway...")
call_command('loaddata', 'jobs_export.json', verbosity=1)

print("\n" + "=" * 60)
print("MIGRATION COMPLETE!")
print("=" * 60)
print(f"\nCheck: https://web-production-ee3d.up.railway.app/admin/")