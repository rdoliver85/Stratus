from django.urls import path
from . import views

app_name = 'public_site'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<uuid:job_id>/', views.job_detail, name='job_detail'),
]