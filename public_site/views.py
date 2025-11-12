from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from jobs.models import Job
from companies.models import Company
from django.db.models import Q

def homepage(request):
    """Landing page with hero section"""
    recent_jobs = Job.objects.filter(status='active').order_by('-created_at')[:6]
    veteran_jobs_count = Job.objects.filter(status='active', is_veteran_friendly=True).count()
    clearance_jobs_count = Job.objects.filter(status='active').exclude(security_clearance='none').count()
    
    context = {
        'recent_jobs': recent_jobs,
        'veteran_jobs_count': veteran_jobs_count,
        'clearance_jobs_count': clearance_jobs_count,
        'total_jobs': Job.objects.filter(status='active').count(),
    }
    return render(request, 'public_site/homepage.html', context)

def job_list(request):
    """Job listing page with filters"""
    jobs = Job.objects.filter(status='active').select_related('company').order_by('-created_at')
    
    # Filters
    veteran_friendly = request.GET.get('veteran_friendly')
    clearance = request.GET.get('clearance')
    location = request.GET.get('location')
    search = request.GET.get('search')
    remote = request.GET.get('remote')
    
    if veteran_friendly:
        jobs = jobs.filter(is_veteran_friendly=True)
    
    if clearance and clearance != 'all':
        jobs = jobs.filter(security_clearance=clearance)
    
    if location:
        jobs = jobs.filter(
            Q(location_city__icontains=location) | 
            Q(location_state__icontains=location)
        )
    
    if remote:
        jobs = jobs.filter(is_remote=True)
    
    if search:
        jobs = jobs.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(company__name__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(jobs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'veteran_friendly': veteran_friendly,
        'clearance': clearance,
        'location': location,
        'search': search,
        'remote': remote,
        'clearance_choices': Job.CLEARANCE_LEVELS,
    }
    return render(request, 'public_site/job_list.html', context)

def job_detail(request, job_id):
    """Individual job detail page"""
    job = get_object_or_404(Job, job_id=job_id, status='active')
    
    # Increment view count
    job.views_count += 1
    job.save(update_fields=['views_count'])
    
    # Get related jobs from same company
    related_jobs = Job.objects.filter(
        company=job.company,
        status='active'
    ).exclude(job_id=job.job_id)[:3]
    
    # Format location
    location_parts = [job.location_city, job.location_state]
    location_display = ', '.join(filter(None, location_parts)) or 'Location not specified'
    
    context = {
        'job': job,
        'related_jobs': related_jobs,
        'location_display': location_display,
    }
    return render(request, 'public_site/job_detail.html', context)