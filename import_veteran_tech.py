import os
import requests
import django
import time
import hashlib

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobs.models import Job
from companies.models import Company
from django.utils.text import slugify
import re

API_CONFIGS = {
    'adzuna': {
        'app_id': 'b9a33838',  # From Adzuna
        'app_key': '2296bf58658e672f8dfb854d7460bc1e',  # From Adzuna
        'base_url': 'https://api.adzuna.com/v1/api/jobs/us/search/',
        'enabled': True,  # Change to True
    },
    'usajobs': {
        'api_key': '6B4ZzOGA0Ae2D2udWTvXbYtDr4dweZ4fbkynLNxDtA0=',  # From USAJobs email
        'user_agent': 'windsoftechnology@gmail.com',  # Your email
        'base_url': 'https://data.usajobs.gov/api/search',
        'enabled': True,  # Change to True
    },
    'jsearch': {
        'api_key': 'eecba37741msh8aab8cab5e05f9ep185a20jsn9877c391a7b3',  # From RapidAPI
        'base_url': 'https://jsearch.p.rapidapi.com/search',
        'enabled': True,  # Change to True
    }
}

# TECHNOLOGY + VETERAN search combinations
TECH_VETERAN_SEARCHES = [
    'veteran software developer',
    'veteran software engineer',
    'military cybersecurity',
    'veteran IT jobs',
    'cleared software engineer',
    'defense contractor developer',
    'veteran cloud engineer',
    'military transition technology',
    'veteran data analyst',
    'cleared DevOps engineer',
    'defense software developer',
    'ts/sci software engineer',
    'veteran network engineer',
    'military intelligence analyst technology',
    'veteran systems administrator',
]

# Technology keywords to filter jobs
TECH_KEYWORDS = [
    'software', 'developer', 'engineer', 'programming', 'coding',
    'python', 'java', 'javascript', 'c++', 'c#', 'sql',
    'cloud', 'aws', 'azure', 'devops', 'kubernetes', 'docker',
    'cybersecurity', 'security', 'network', 'systems',
    'data', 'analyst', 'database', 'big data', 'machine learning',
    'web', 'mobile', 'frontend', 'backend', 'full stack',
    'agile', 'scrum', 'ci/cd', 'api', 'rest', 'microservices',
    'infrastructure', 'linux', 'windows server', 'vmware',
    'cisco', 'networking', 'firewall', 'penetration testing'
]

# Exclude non-tech jobs
EXCLUDE_KEYWORDS = [
    'nurse', 'nursing', 'medical', 'healthcare', 'physician',
    'social worker', 'therapist', 'counselor', 'teacher',
    'driver', 'warehouse', 'retail', 'sales', 'customer service',
    'administrative assistant', 'receptionist', 'cleaner'
]

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = ' '.join(text.split())
    return text

def is_tech_job(title, description):
    """Verify job is actually technology-related"""
    text = (title + ' ' + description).lower()
    
    # Check if it contains excluded keywords (non-tech)
    if any(exclude in text for exclude in EXCLUDE_KEYWORDS):
        return False
    
    # Must contain at least one tech keyword
    return any(tech in text for tech in TECH_KEYWORDS)

def generate_job_hash(title, company):
    unique_string = f"{title.lower()}{company.lower()}"
    return hashlib.md5(unique_string.encode()).hexdigest()

def get_or_create_company(company_name):
    if not company_name:
        company_name = "Unknown Company"
    slug = slugify(company_name)
    company, _ = Company.objects.get_or_create(
        slug=slug,
        defaults={'name': company_name}
    )
    return company

def detect_clearance(text):
    text_lower = text.lower()
    if 'ts/sci' in text_lower or 'tssci' in text_lower:
        return 'ts_sci'
    elif 'top secret' in text_lower:
        return 'top_secret'
    elif 'secret clearance' in text_lower:
        return 'secret'
    elif 'confidential clearance' in text_lower:
        return 'confidential'
    return 'none'

def import_tech_veteran_adzuna(search_term, max_results=30):
    config = API_CONFIGS['adzuna']
    if not config['enabled']:
        return 0
    
    imported = 0
    print(f"\n🔍 Searching: '{search_term}'...")
    
    url = f"{config['base_url']}1"
    params = {
        'app_id': config['app_id'],
        'app_key': config['app_key'],
        'results_per_page': 50,
        'what': search_term,
        'where': 'United States'
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        for job_data in data.get('results', []):
            try:
                title = job_data.get('title', 'Position')
                description = clean_text(job_data.get('description', ''))
                
                # FILTER: Only import if it's actually a tech job
                if not is_tech_job(title, description):
                    continue
                
                company_name = job_data.get('company', {}).get('display_name', 'Company')
                
                job_hash = generate_job_hash(title, company_name)
                if Job.objects.filter(slug__contains=job_hash[:8]).exists():
                    continue
                
                company = get_or_create_company(company_name)
                slug = slugify(f"{title}-{job_hash[:8]}")
                
                location_data = job_data.get('location', {})
                location_str = location_data.get('display_name', '')
                parts = location_str.split(',')
                city = parts[0].strip() if parts else ''
                state = parts[1].strip() if len(parts) > 1 else ''
                
                clearance = detect_clearance(title + ' ' + description)
                
                text_combined = (title + ' ' + description + ' ' + company_name).lower()
                is_vet_friendly = any(kw in text_combined for kw in ['veteran', 'military', 'clearance', 'defense'])
                
                Job.objects.create(
                    title=title[:200],
                    slug=slug,
                    description=description,
                    company=company,
                    employment_type='full_time',
                    experience_level='mid_level',
                    salary_min=job_data.get('salary_min'),
                    salary_max=job_data.get('salary_max'),
                    location_city=city[:100],
                    location_state=state[:50],
                    location_country='US',
                    is_remote='remote' in title.lower(),
                    status='active',
                    is_veteran_friendly=is_vet_friendly,
                    security_clearance=clearance,
                    military_skills_valued='Technical skills, security clearance, leadership' if is_vet_friendly else '',
                    application_url=job_data.get('redirect_url', '')  # ADD THIS LINE
                )
                
                imported += 1
                print(f"   ✓ [{imported}] {title}")
                
                if imported >= max_results:
                    break
                    
            except Exception as e:
                continue
        
        time.sleep(1)
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    return imported

def import_tech_veteran_jsearch(search_term, max_results=25):
    config = API_CONFIGS['jsearch']
    if not config['enabled']:
        return 0
    
    imported = 0
    print(f"\n🔍 JSearch: '{search_term}'...")
    
    headers = {
        'X-RapidAPI-Key': config['api_key'],
        'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
    }
    
    params = {
        'query': f'{search_term} United States',
        'page': '1',
        'num_pages': '1'
    }
    
    try:
        response = requests.get(config['base_url'], headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        for job_data in data.get('data', [])[:max_results]:
            try:
                title = job_data.get('job_title', 'Position')
                description = clean_text(job_data.get('job_description', ''))
                
                # FILTER: Tech jobs only
                if not is_tech_job(title, description):
                    continue
                
                company_name = job_data.get('employer_name', 'Company')
                
                job_hash = generate_job_hash(title, company_name)
                if Job.objects.filter(slug__contains=job_hash[:8]).exists():
                    continue
                
                company = get_or_create_company(company_name)
                slug = slugify(f"{title}-{job_hash[:8]}")
                
                clearance = detect_clearance(title + ' ' + description)
                
                text_combined = (title + ' ' + description).lower()
                is_vet_friendly = any(kw in text_combined for kw in ['veteran', 'military', 'clearance', 'defense'])
                
                Job.objects.create(
                    title=title[:200],
                    slug=slug,
                    description=description,
                    company=company,
                    employment_type='full_time',
                    experience_level='mid_level',
                    salary_min=job_data.get('job_min_salary'),
                    salary_max=job_data.get('job_max_salary'),
                    location_city=job_data.get('job_city', '')[:100],
                    location_state=job_data.get('job_state', '')[:50],
                    location_country='US',
                    is_remote=job_data.get('job_is_remote', False),
                    status='active',
                    is_veteran_friendly=is_vet_friendly,
                    security_clearance=clearance,
                    military_skills_valued='Technology and military experience valued' if is_vet_friendly else '',
		    application_url=job_data.get('job_apply_link', '')
                )
                
                imported += 1
                print(f"   ✓ [{imported}] {title}")
                
            except Exception as e:
                continue
        
        time.sleep(2)
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    return imported

if __name__ == '__main__':
    print("\n" + "="*70)
    print(" 🎖️💻 VETERAN TECHNOLOGY JOBS IMPORT")
    print(" Target: Tech jobs for military veterans with clearances")
    print("="*70)
    
    start_count = Job.objects.count()
    total_imported = 0
    
    # Import from tech+veteran search terms
    for search_term in TECH_VETERAN_SEARCHES:
        count = import_tech_veteran_adzuna(search_term, max_results=20)
        total_imported += count
        if count > 0:
            time.sleep(2)
    
    # JSearch tech veteran jobs
    jsearch_terms = [
        'veteran software developer',
        'cleared software engineer',
        'military cybersecurity',
        'veteran IT specialist'
    ]
    
    for search_term in jsearch_terms:
        count = import_tech_veteran_jsearch(search_term, max_results=20)
        total_imported += count
        time.sleep(3)
    
    # Final stats
    end_count = Job.objects.count()
    vet_count = Job.objects.filter(is_veteran_friendly=True).count()
    
    print("\n" + "="*70)
    print(" 🎖️💻 TECH VETERAN IMPORT COMPLETE")
    print(f" Tech Jobs Added: {total_imported}")
    print(f" Total Jobs: {start_count} → {end_count}")
    print(f" Veteran-Friendly Tech: {vet_count}")
    print("="*70 + "\n")