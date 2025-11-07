import os
import requests
import django
import time
from datetime import datetime

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

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = ' '.join(text.split())
    return text[:5000]

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
    """Detect security clearance requirements"""
    text_lower = text.lower()
    if 'ts/sci' in text_lower or 'tssci' in text_lower:
        return 'ts_sci'
    elif 'top secret' in text_lower:
        return 'top_secret'
    elif 'secret clearance' in text_lower:
        return 'secret'
    elif 'confidential' in text_lower and 'clearance' in text_lower:
        return 'confidential'
    return 'none'

def import_veteran_jobs_adzuna():
    """Import veteran-focused jobs from Adzuna"""
    config = API_CONFIGS['adzuna']
    if not config['enabled']:
        return 0
    
    print("\n" + "="*60)
    print("IMPORTING VETERAN-FOCUSED JOBS FROM ADZUNA")
    print("="*60)
    
    veteran_searches = [
        'veteran jobs',
        'military transition',
        'security clearance',
        'defense contractor',
        'former military'
    ]
    
    imported = 0
    
    for search_term in veteran_searches:
        print(f"\nSearching: {search_term}")
        
        url = f"{config['base_url']}1"
        params = {
            'app_id': config['app_id'],
            'app_key': config['app_key'],
            'results_per_page': 30,
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
                    company_name = job_data.get('company', {}).get('display_name', 'Company')
                    description = clean_text(job_data.get('description', ''))
                    
                    # Skip if already exists
                    if Job.objects.filter(title=title, company__name=company_name).exists():
                        continue
                    
                    company = get_or_create_company(company_name)
                    
                    slug = slugify(title)
                    counter = 1
                    while Job.objects.filter(slug=slug).exists():
                        slug = f"{slugify(title)}-{counter}"
                        counter += 1
                    
                    location_data = job_data.get('location', {})
                    location_str = location_data.get('display_name', '')
                    city = location_str.split(',')[0] if location_str else ''
                    
                    # Detect clearance
                    clearance = detect_clearance(title + ' ' + description)
                    
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
                        location_state='',
                        location_country='US',
                        is_remote='remote' in title.lower(),
                        status='active',
                        is_veteran_friendly=True,
                        security_clearance=clearance
                    )
                    
                    imported += 1
                    print(f"✓ [{imported}] {title}")
                    
                except Exception as e:
                    continue
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    return imported

def import_veteran_jobs_usajobs():
    """Import veteran preference jobs from USAJobs"""
    config = API_CONFIGS['usajobs']
    if not config['enabled']:
        return 0
    
    print("\n" + "="*60)
    print("IMPORTING VETERAN PREFERENCE JOBS FROM USAJOBS")
    print("="*60)
    
    headers = {
        'Host': 'data.usajobs.gov',
        'User-Agent': config['user_agent'],
        'Authorization-Key': config['api_key']
    }
    
    imported = 0
    
    params = {
        'Keyword': 'veteran',
        'ResultsPerPage': 50,
        'Page': 1
    }
    
    try:
        response = requests.get(config['base_url'], headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        for item in data.get('SearchResult', {}).get('SearchResultItems', []):
            try:
                job_data = item.get('MatchedObjectDescriptor', {})
                title = job_data.get('PositionTitle', 'Government Position')
                org_name = job_data.get('OrganizationName', 'U.S. Government')
                
                if Job.objects.filter(title=title, company__name=org_name).exists():
                    continue
                
                company = get_or_create_company(org_name)
                
                slug = slugify(title)
                counter = 1
                while Job.objects.filter(slug=slug).exists():
                    slug = f"{slugify(title)}-{counter}"
                    counter += 1
                
                qualifications = job_data.get('QualificationSummary', '')
                
                Job.objects.create(
                    title=title[:200],
                    slug=slug,
                    description=qualifications[:5000],
                    company=company,
                    employment_type='full_time',
                    experience_level='mid_level',
                    location_city='Washington',
                    location_state='DC',
                    location_country='US',
                    status='active',
                    is_veteran_friendly=True,
                    veteran_preference=True,
                    security_clearance='secret'
                )
                
                imported += 1
                print(f"✓ [{imported}] {title}")
                
            except Exception as e:
                continue
    
    except Exception as e:
        print(f"Error: {e}")
    
    return imported