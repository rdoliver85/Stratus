from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Job, FavoriteJob, JobApplication

@login_required
def add_favorite(request, job_id):
    """Add a job to user's favorites"""
    job = get_object_or_404(Job, job_id=job_id)
    
    # Check if already favorited
    favorite, created = FavoriteJob.objects.get_or_create(
        user=request.user,
        job=job
    )
    
    if created:
        messages.success(request, f"'{job.title}' added to your saved jobs!")
    else:
        messages.info(request, "This job is already in your saved jobs.")
    
    # Redirect back to the previous page
    return redirect(request.META.get('HTTP_REFERER', 'public_site:job_list'))

@login_required
def remove_favorite(request, job_id):
    """Remove a job from user's favorites"""
    job = get_object_or_404(Job, job_id=job_id)
    
    try:
        favorite = FavoriteJob.objects.get(user=request.user, job=job)
        favorite.delete()
        messages.success(request, f"'{job.title}' removed from your saved jobs.")
    except FavoriteJob.DoesNotExist:
        messages.error(request, "This job was not in your saved jobs.")
    
    # Redirect back to the previous page
    return redirect(request.META.get('HTTP_REFERER', 'public_site:job_list'))

@login_required
def saved_jobs(request):
    """Display user's saved/favorited jobs"""
    favorites = FavoriteJob.objects.filter(user=request.user).select_related('job', 'job__company')
    
    context = {
        'favorites': favorites,
    }
    return render(request, 'jobs/saved_jobs.html', context)

@login_required
def mark_applied(request, job_id):
    """Mark a job as applied"""
    job = get_object_or_404(Job, job_id=job_id)
    
    application, created = JobApplication.objects.get_or_create(
        user=request.user,
        job=job
    )
    
    if created:
        messages.success(request, f"Marked '{job.title}' as applied!")
    else:
        messages.info(request, "You already marked this job as applied.")
    
    # Redirect back to the job detail page
    return redirect('public_site:job_detail', job_id=job_id)

@login_required
def my_applications(request):
    """Display user's job applications"""
    applications = JobApplication.objects.filter(user=request.user).select_related('job', 'job__company')
    
    context = {
        'applications': applications,
    }
    return render(request, 'jobs/my_applications.html', context)