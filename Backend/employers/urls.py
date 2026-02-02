from django.urls import path
from . import views

app_name = 'employers'

urlpatterns = [
    # Employer profile endpoints
    path('profile/', views.EmployerProfileAPI.as_view(), name='employer_profile'),
    path('dashboard/', views.EmployerDashboardAPI.as_view(), name='employer_dashboard'),
    
    # Job management endpoints
    path('jobs/', views.EmployerJobsAPI.as_view(), name='employer_jobs'),
    path('jobs/create/', views.JobCreateAPI.as_view(), name='job_create'),
    path('jobs/<int:job_id>/update/', views.JobUpdateAPI.as_view(), name='job_update'),
    path('jobs/<int:job_id>/toggle-status/', views.JobToggleStatusAPI.as_view(), name='job_toggle_status'),
    path('jobs/<int:job_id>/activate/', views.JobActivateAPI.as_view(), name='job_activate'),
    path('jobs/<int:job_id>/deactivate/', views.JobDeactivateAPI.as_view(), name='job_deactivate'),
    
    # Application management endpoints
    path('jobs/<int:job_id>/applications/', views.JobApplicationsAPI.as_view(), name='job_applications'),
    path('applications/<int:app_id>/shortlist/', views.ShortlistCandidateAPI.as_view(), name='shortlist_candidate'),
    path('applications/<int:app_id>/reject/', views.RejectCandidateAPI.as_view(), name='reject_candidate'),
]