from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('favorite/<uuid:job_id>/', views.add_favorite, name='add_favorite'),
    path('unfavorite/<uuid:job_id>/', views.remove_favorite, name='remove_favorite'),
    path('saved/', views.saved_jobs, name='saved_jobs'),
    path('mark-applied/<uuid:job_id>/', views.mark_applied, name='mark_applied'),
    path('applications/', views.my_applications, name='my_applications'),
]