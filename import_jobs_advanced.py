# Multi-Source Job API Aggregator
# Advanced job import system for Master's demonstration
# Aggregates jobs from multiple APIs with deduplication and normalization

import os
import requests
import django
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from jobs.models import Job
from companies.models import Company
from django.utils.text import slugify
import re

# ================================
# API CONFIGURATIONS
# ================================

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
        'enabled': True,
    },
    'jsearch': {
        'api_key': 'eecba37741msh8aab8cab5e05f9ep185a20jsn9877c391a7b3',  # From RapidAPI
        'base_url': 'https://jsearch.p.rapidapi.com/search',
        'enabled': False,
    }
}

# ================================
# UTILITY FUNCTIONS
# ================================

def clean_html(text):
    """Remove HTML tags and clean text"""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)
    return text  # Limit length for database

def generate_job_hash(title, company, location):
    """Generate unique hash for duplicate detection"""
    unique_string = f"{title.lower()}{company.lower()}{location.lower()}"
    return hashlib.md5(unique_string.encode()).hexdigest()

def normalize_salary(salary_str):
    """Extract salary from various formats"""
    if not salary_str:
        return None, None
    
    # Remove non-numeric except decimal points and hyphens
    salary_str = re.sub(r'[^\d.\-]', '', str(salary_str))
    
    if '-' in salary_str:
        parts = salary_str.split('-')
        try:
            return int(float(parts[0])), int(float(parts[1]))
        except:
            return None, None
    
    try:
        salary = int(float(salary_str))
        return salary, salary
    except:
        return None, None

def determine_employment_type(title, description=''):
    """Intelligently determine employment type from text"""
    text = (title + ' ' + description).lower()
    
    if any(word in text for word in ['part time', 'part-time', 'parttime']):
        return 'part_time'
    elif any(word in text for word in ['contract', 'contractor', 'freelance']):
        return 'contract'
    elif any(word in text for word in ['temp', 'temporary', 'seasonal']):
        return 'temporary'
    elif any(word in text for word in ['intern', 'internship', 'co-op', 'coop']):
        return 'internship'
    else:
        return 'full_time'

def determine_experience_level(title, description=''):
    """Intelligently determine experience level from text"""
    text = (title + ' ' + description).lower()
    
    if any(word in text for word in ['senior', 'sr.', 'lead', 'principal', 'staff', 'architect']):
        return 'senior_level'
    elif any(word in text for word in ['junior', 'jr.', 'entry', 'entry-level', 'graduate', 'associate']):
        return 'entry_level'
    elif any(word in text for word in ['director', 'vp', 'vice president', 'chief', 'head of', 'executive']):
        return 'executive'
    else:
        return 'mid_level'

def get_or_create_company(company_name, company_data=None):
    """Get existing company or create new one with enhanced data"""
    if not company_name:
        company_name = "Unknown Company"
    
    slug = slugify(company_name)
    
    # Check if company exists
    company = Company.objects.filter(slug=slug).first()
    if company:
        return company
    
    # Create new company with available data
    company = Company.objects.create(
        name=company_name,
        slug=slug,
        description=company_data.get('description', f'{company_name} is hiring talented professionals.') if company_data else f'{company_name} is hiring.',
        website_url=company_data.get('website', '') if company_data else '',
        industry=company_data.get('industry', '') if company_data else '',
    )
    
    return company

# ================================
# ADZUNA API INTEGRATION
# ================================

def import_from_adzuna(search_term='software', location='United States', max_results=100):
    """Import jobs from Adzuna API"""
    
    config = API_CONFIGS['adzuna']
    if not config['enabled']:
        print("❌ Adzuna API not configured. Set credentials in API_CONFIGS.")
        return 0
    
    print(f"\n{'='*60}")
    print(f"IMPORTING FROM ADZUNA")
    print(f"Search: {search_term} in {location}")
    print(f"{'='*60}")
    
    imported = 0
    page = 1
    results_per_page = 50
    
    while imported < max_results:
        url = f"{config['base_url']}{page}"
        params = {
            'app_id': config['app_id'],
            'app_key': config['app_key'],
            'results_per_page': results_per_page,
            'what': search_term,
            'where': location,
            'content-type': 'application/json'
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
                    title = job_data.get('title', 'Untitled Position')
                    company_name = job_data.get('company', {}).get('display_name', 'Unknown Company')
                    location_str = job_data.get('location', {}).get('display_name', location)
                    
                    # Check for duplicates
                    job_hash = generate_job_hash(title, company_name, location_str)
                    if Job.objects.filter(description__contains=job_hash[:16]).exists():
                        continue
                    
                    description = clean_html(job_data.get('description', ''))
                    
                    # Create company
                    company = get_or_create_company(company_name)
                    
                    # Generate unique slug
                    base_slug = slugify(title)
                    slug = base_slug
                    counter = 1
                    while Job.objects.filter(slug=slug).exists():
                        slug = f"{base_slug}-{counter}"
                        counter += 1
                    
                    # Parse location
                    location_parts = location_str.split(',')
                    city = location_parts[0].strip() if location_parts else ''
                    state = location_parts[1].strip() if len(location_parts) > 1 else ''
                    
                    # Create job
                    job = Job.objects.create(
                        title=title[:200],
                        slug=slug,
                        description=f"{description}\n\nSource: Adzuna (ID: {job_hash[:16]})",
                        company=company,
                        employment_type=determine_employment_type(title, description),
                        experience_level=determine_experience_level(title, description),
                        salary_min=job_data.get('salary_min'),
                        salary_max=job_data.get('salary_max'),
                        location_city=city[:100],
                        location_state=state[:50],
                        location_country='US',
                        latitude=job_data.get('latitude'),
                        longitude=job_data.get('longitude'),
                        is_remote='remote' in title.lower() or 'remote' in description.lower(),
                        status='active',
			application_url=job_data.get('redirect_url', '')
                    )
                    
                    imported += 1
                    print(f"✓ [{imported}] {title} - {company_name}")
                    
                    if imported >= max_results:
                        break
                        
                except Exception as e:
                    print(f"✗ Error importing job: {str(e)}")
                    continue
            
            page += 1
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"❌ API request failed: {str(e)}")
            break
    
    print(f"\n✅ Imported {imported} jobs from Adzuna\n")
    return imported

# ================================
# USAJOBS API INTEGRATION
# ================================

def import_veteran_jobs_usajobs():
    """Import tech jobs from USAJobs using job family codes"""
    config = API_CONFIGS['usajobs']
    if not config['enabled']:
        return 0
    
    print("\n" + "="*60)
    print("IMPORTING TECH JOBS FROM USAJOBS")
    print("="*60)
    
    headers = {
        'Host': 'data.usajobs.gov',
        'User-Agent': config['user_agent'],
        'Authorization-Key': config['api_key']
    }
    
    imported = 0
    
    # Tech job family codes
    tech_codes = ['2210', '1550', '0854']
    
    for code in tech_codes:
        params = {
            'JobCategoryCode': code,
            'ResultsPerPage': 100,
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
                    
                    qualifications = clean_html(job_data.get('QualificationSummary', ''))
                    
                    Job.objects.create(
                        title=title[:200],
                        slug=slug,
                        description=qualifications,
                        company=company,
                        employment_type='full_time',
                        experience_level='mid_level',
                        location_city=job_data.get('PositionLocationDisplay', 'Washington')[:100],
                        location_state='DC',
                        location_country='US',
                        status='active',
                        application_url=job_data.get('PositionURI', '')
                    )
                    
                    imported += 1
                    print(f"✓ [{imported}] {title}")
                    
                except Exception as e:
                    continue
            
            time.sleep(1)
        
        except Exception as e:
            print(f"Error with code {code}: {e}")
    
    return imported

# ================================
# JSEARCH API INTEGRATION
# ================================

def import_from_jsearch(query='Python developer', max_results=100):
    """Import jobs from JSearch (RapidAPI)"""
    
    config = API_CONFIGS['jsearch']
    if not config['enabled']:
        print("❌ JSearch API not configured. Set credentials in API_CONFIGS.")
        return 0
    
    print(f"\n{'='*60}")
    print(f"IMPORTING FROM JSEARCH")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    imported = 0
    page = 1
    
    headers = {
        'X-RapidAPI-Key': config['api_key'],
        'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
    }
    
    while imported < max_results:
        params = {
            'query': query,
            'page': page,
            'num_pages': '1'
        }
        
        try:
            response = requests.get(config['base_url'], headers=headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            jobs_data = data.get('data', [])
            if not jobs_data:
                break
            
            for job_data in jobs_data:
                try:
                    title = job_data.get('job_title', 'Position')
                    company_name = job_data.get('employer_name', 'Company')
                    
                    # Check for duplicates
                    location = job_data.get('job_city', '') + job_data.get('job_state', '')
                    job_hash = generate_job_hash(title, company_name, location)
                    if Job.objects.filter(description__contains=job_hash[:16]).exists():
                        continue
                    
                    company = get_or_create_company(company_name)
                    
                    base_slug = slugify(title)
                    slug = base_slug
                    counter = 1
                    while Job.objects.filter(slug=slug).exists():
                        slug = f"{base_slug}-{counter}"
                        counter += 1
                    
                    description = clean_html(job_data.get('job_description', ''))
                    
                    # Parse salary
                    salary_min, salary_max = None, None
                    if job_data.get('job_min_salary'):
                        salary_min = int(job_data['job_min_salary'])
                    if job_data.get('job_max_salary'):
                        salary_max = int(job_data['job_max_salary'])
                    
                    job = Job.objects.create(
                        title=title[:200],
                        slug=slug,
                        description=f"{description}\n\nSource: JSearch (ID: {job_hash[:16]})",
                        company=company,
                        employment_type=determine_employment_type(title, description),
                        experience_level=determine_experience_level(title, description),
                        salary_min=salary_min,
                        salary_max=salary_max,
                        location_city=job_data.get('job_city', '')[:100],
                        location_state=job_data.get('job_state', '')[:50],
                        location_country='US',
                        latitude=job_data.get('job_latitude'),
                        longitude=job_data.get('job_longitude'),
                        is_remote=job_data.get('job_is_remote', False),
                        status='active',
			application_url=job_data.get('job_apply_link', '')
                    )
                    
                    imported += 1
                    print(f"✓ [{imported}] {title} - {company_name}")
                    
                    if imported >= max_results:
                        break
                        
                except Exception as e:
                    print(f"✗ Error importing job: {str(e)}")
                    continue
            
            page += 1
            time.sleep(1)  # RapidAPI rate limit
            
        except Exception as e:
            print(f"❌ API request failed: {str(e)}")
            break
    
    print(f"\n✅ Imported {imported} jobs from JSearch\n")
    return imported

# ================================
# MAIN AGGREGATION FUNCTION
# ================================

def aggregate_jobs_from_all_sources():
    """Import jobs from all configured API sources"""
    
    print("\n" + "="*60)
    print(" MULTI-SOURCE JOB AGGREGATION SYSTEM")
    print(" Master's Demonstration - Advanced Job Platform")
    print("="*60)
    
    total_imported = 0
    
    # Diverse tech search terms
    adzuna_searches = [
        'software engineer',
        'data analyst', 
        'cloud engineer',
        'devops engineer',
        'cybersecurity analyst',
        'network engineer',
        'full stack developer',
        'backend developer',
        'frontend developer',
        'machine learning engineer',
        'data scientist',
        'systems administrator',
        'database administrator',
        'security engineer'
    ]
    
    jsearch_queries = [
        'software developer united states',
        'data engineer united states',
        'cloud architect united states',
        'python developer united states',
        'java developer united states',
        'javascript developer united states',
        'react developer united states',
        'aws engineer united states',
        'kubernetes engineer united states',
        'ai engineer united states'
    ]
    
    # Import from Adzuna with multiple searches
    if API_CONFIGS['adzuna']['enabled']:
        for search_term in adzuna_searches:
            count = import_from_adzuna(search_term, 'United States', 30)
            total_imported += count
            time.sleep(2)
    
    # Import from USAJobs (tech codes)
    if API_CONFIGS['usajobs']['enabled']:
        total_imported += import_veteran_jobs_usajobs()
        time.sleep(2)
    
    # Import from JSearch with multiple searches
    if API_CONFIGS['jsearch']['enabled']:
        for query in jsearch_queries:
            count = import_from_jsearch(query, 30)
            total_imported += count
            time.sleep(3)
    
    # Final summary
    print("\n" + "="*60)
    print(f" AGGREGATION COMPLETE")
    print(f" Total Jobs Imported: {total_imported}")
    print(f" Total Companies: {Company.objects.count()}")
    print(f" Active Jobs: {Job.objects.filter(status='active').count()}")
    print("="*60 + "\n")
    
    return total_imported

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'adzuna':
            import_from_adzuna('software', 'United States', 100)
        elif command == 'usajobs':
            import_from_usajobs('developer', 50)
        elif command == 'jsearch':
            import_from_jsearch('Python developer', 100)
        elif command == 'all':
            aggregate_jobs_from_all_sources()
        else:
            print("Usage: python import_jobs_advanced.py [adzuna|usajobs|jsearch|all]")
    else:
        # Default: aggregate from all sources
        aggregate_jobs_from_all_sources()