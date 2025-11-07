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

# Veteran-focused search terms
VETERAN_SEARCH_TERMS = [
    'veteran jobs',
    'military transition',
    'former military',
    'security clearance',
    'defense contractor',
    'cleared jobs',
    'top secret clearance',
    'ts/sci jobs',
    'military experience',
    'veteran friendly employer',
    'hire veterans',
    'military spouse',
    'DOD contractor',
    'defense industry',
    'veteran preference',
]

# Known veteran-friendly companies
VETERAN_COMPANIES = [
    'Lockheed Martin',
    'Raytheon',
    'Boeing',
    'Northrop Grumman',
    'General Dynamics',
    'CACI',
    'Booz Allen Hamilton',
    'Leidos',
    'BAE Systems',
    'L3Harris',
]

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = ' '.join(text.split())
    return text[:5000]

def generate_job_hash(title, company):
    """Generate hash to detect duplicates"""
    unique_string = f"{title.lower()}{company.lower()}"
    return hashlib.md5(unique_string.encode()).hexdigest()

def get_or_create_company(company_name, is_defense=False):
    if not company_name:
        company_name = "Unknown Company"
    
    slug = slugify(company_name)
    company, created = Company.objects.get_or_create(
        slug=slug,
        defaults={
            'name': company_name,
            'description': f'{company_name} - Veteran-friendly employer' if is_defense else company_name
        }
    )
    return company

def detect_clearance(text):
    """Detect security clearance level"""
    text_lower = text.lower()
    if 'ts/sci' in text_lower or 'tssci' in text_lower or 'ts-sci' in text_lower:
        return 'ts_sci'
    elif 'top secret' in text_lower:
        return 'top_secret'
    elif 'secret clearance' in text_lower or 'secret security' in text_lower:
        return 'secret'
    elif 'confidential clearance' in text_lower:
        return 'confidential'
    return 'none'

def extract_mos_codes(text):
    """Extract potential MOS codes from job description"""
    # Common MOS patterns: 11B, 68W, 25B, etc.
    mos_pattern = r'\b\d{2}[A-Z]\b'
    matches = re.findall(mos_pattern, text)
    return ', '.join(set(matches)) if matches else ''

def import_from_adzuna_veteran(search_term, max_results=50):
    """Import veteran jobs from Adzuna with specific search term"""
    config = API_CONFIGS['adzuna']
    if not config['enabled']:
        return 0
    
    imported = 0
    page = 1
    
    print(f"\n🔍 Adzuna: Searching '{search_term}'...")
    
    while imported < max_results:
        url = f"{config['base_url']}{page}"
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
            
            jobs_data = data.get('results', [])
            if not jobs_data:
                break
            
            for job_data in jobs_data:
                try:
                    title = job_data.get('title', 'Position')
                    company_name = job_data.get('company', {}).get('display_name', 'Company')
                    
                    # Skip duplicates
                    job_hash = generate_job_hash(title, company_name)
                    if Job.objects.filter(slug__contains=job_hash[:8]).exists():
                        continue
                    
                    description = clean_text(job_data.get('description', ''))
                    
                    # Determine if defense/veteran company
                    is_defense = any(vet_comp.lower() in company_name.lower() for vet_comp in VETERAN_COMPANIES)
                    company = get_or_create_company(company_name, is_defense)
                    
                    slug = slugify(f"{title}-{job_hash[:8]}")
                    
                    location_data = job_data.get('location', {})
                    location_str = location_data.get('display_name', '')
                    parts = location_str.split(',')
                    city = parts[0].strip() if parts else ''
                    state = parts[1].strip() if len(parts) > 1 else ''
                    
                    clearance = detect_clearance(title + ' ' + description)
                    mos_codes = extract_mos_codes(description)
                    
                    # Determine veteran-specific attributes
                    text_combined = (title + ' ' + description + ' ' + company_name).lower()
                    is_vet_friendly = any(keyword in text_combined for keyword in ['veteran', 'military', 'clearance', 'defense', 'dod'])
                    has_vet_pref = 'veteran preference' in text_combined or 'veterans preference' in text_combined
                    
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
                        latitude=location_data.get('latitude'),
                        longitude=location_data.get('longitude'),
                        is_remote='remote' in title.lower(),
                        status='active',
                        is_veteran_friendly=is_vet_friendly,
                        veteran_preference=has_vet_pref,
                        security_clearance=clearance,
                        applicable_mos_codes=mos_codes,
                        military_skills_valued='Leadership, discipline, technical skills valued' if is_vet_friendly else ''
                    )
                    
                    imported += 1
                    print(f"   ✓ [{imported}] {title} - {company_name}")
                    
                    if imported >= max_results:
                        break
                        
                except Exception as e:
                    continue
            
            page += 1
            time.sleep(1)
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
            break
    
    return imported

def import_from_jsearch_veteran(search_term, max_results=30):
    """Import veteran jobs from JSearch"""
    config = API_CONFIGS['jsearch']
    if not config['enabled']:
        return 0
    
    imported = 0
    
    print(f"\n🔍 JSearch: Searching '{search_term}'...")
    
    headers = {
        'X-RapidAPI-Key': config['api_key'],
        'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
    }
    
    params = {
        'query': f'{search_term} United States',
        'page': '1',
        'num_pages': '2'
    }
    
    try:
        response = requests.get(config['base_url'], headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        for job_data in data.get('data', [])[:max_results]:
            try:
                title = job_data.get('job_title', 'Position')
                company_name = job_data.get('employer_name', 'Company')
                
                job_hash = generate_job_hash(title, company_name)
                if Job.objects.filter(slug__contains=job_hash[:8]).exists():
                    continue
                
                description = clean_text(job_data.get('job_description', ''))
                
                is_defense = any(vet_comp.lower() in company_name.lower() for vet_comp in VETERAN_COMPANIES)
                company = get_or_create_company(company_name, is_defense)
                
                slug = slugify(f"{title}-{job_hash[:8]}")
                
                clearance = detect_clearance(title + ' ' + description)
                mos_codes = extract_mos_codes(description)
                
                text_combined = (title + ' ' + description + ' ' + company_name).lower()
                is_vet_friendly = any(keyword in text_combined for keyword in ['veteran', 'military', 'clearance', 'defense'])
                
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
                    applicable_mos_codes=mos_codes,
                    military_skills_valued='Military experience valued' if is_vet_friendly else ''
                )
                
                imported += 1
                print(f"   ✓ [{imported}] {title} - {company_name}")
                
            except Exception as e:
                continue
        
        time.sleep(2)
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    return imported

def import_veteran_companies_directly():
    """Search for jobs at known veteran-friendly companies"""
    print(f"\n🎯 Targeting Veteran-Friendly Defense Contractors...")
    
    total = 0
    for company in VETERAN_COMPANIES[:5]:  # Top 5 to avoid rate limits
        print(f"\n   Company: {company}")
        count = import_from_adzuna_veteran(company, max_results=20)
        total += count
        time.sleep(2)
    
    return total

if __name__ == '__main__':
    print("\n" + "="*70)
    print(" 🎖️  AGGRESSIVE VETERAN-FOCUSED JOB IMPORT")
    print(" Target: 150-200 Additional Veteran Jobs")
    print("="*70)
    
    start_count = Job.objects.count()
    total_imported = 0
    
    # Import from various veteran search terms
    for search_term in VETERAN_SEARCH_TERMS[:10]:  # Top 10 terms
        count = import_from_adzuna_veteran(search_term, max_results=15)
        total_imported += count
        if count > 0:
            time.sleep(2)
    
    # Import veteran jobs from JSearch
    for search_term in ['veteran jobs', 'military transition', 'security clearance', 'defense contractor']:
        count = import_from_jsearch_veteran(search_term, max_results=25)
        total_imported += count
        time.sleep(3)
    
    # Target specific veteran-friendly companies
    company_jobs = import_veteran_companies_directly()
    total_imported += company_jobs
    
    # Final stats
    end_count = Job.objects.count()
    vet_count = Job.objects.filter(is_veteran_friendly=True).count()
    clearance_count = Job.objects.exclude(security_clearance='none').count()
    
    print("\n" + "="*70)
    print(" 🎖️  IMPORT COMPLETE")
    print(f" Jobs Added: {total_imported}")
    print(f" Total Jobs: {start_count} → {end_count}")
    print(f" Veteran-Friendly: {vet_count} ({int(vet_count/end_count*100)}%)")
    print(f" With Clearance: {clearance_count}")
    print("="*70 + "\n")