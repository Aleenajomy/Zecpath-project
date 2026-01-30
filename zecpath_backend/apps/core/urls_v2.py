from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, viewsets

# Router for ViewSets
router = DefaultRouter()
router.register(r'jobs', viewsets.JobViewSet, basename='job')
router.register(r'users', viewsets.UserViewSet, basename='user')
router.register(r'applications', viewsets.ApplicationViewSet, basename='application')
router.register(r'candidates', viewsets.CandidateViewSet, basename='candidate')
router.register(r'employers', viewsets.EmployerViewSet, basename='employer')

urlpatterns = [
    # Authentication endpoints
    path('', views.home_api, name='home_api'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    
    # Legacy API views (keeping for backward compatibility)
    path('jobs/list/', views.JobListAPI.as_view(), name='job_list'),
    path('jobs/create/', views.JobCreateAPI.as_view(), name='job_create'),
    path('jobs/<int:job_id>/update/', views.JobUpdateAPI.as_view(), name='job_update'),
    path('jobs/<int:job_id>/apply/', views.JobApplicationAPI.as_view(), name='job_apply'),
    
    # Profile endpoints
    path('profile/candidate/', views.CandidateProfileAPI.as_view(), name='candidate_profile'),
    path('profile/employer/', views.EmployerProfileAPI.as_view(), name='employer_profile'),
    
    # Resume endpoints
    path('resume/upload/', views.ResumeUploadAPI.as_view(), name='resume_upload'),
    path('resume/delete/', views.ResumeDeleteAPI.as_view(), name='resume_delete'),
    path('resume/download/', views.ResumeDownloadAPI.as_view(), name='resume_download'),
    path('resume/download/<int:candidate_id>/', views.ResumeDownloadAPI.as_view(), name='resume_download_by_id'),
    
    # Admin endpoints
    path('admin/dashboard/', views.AdminDashboardAPI.as_view(), name='admin_dashboard'),
    path('admin/users/', views.UserTestAPI.as_view(), name='admin_users'),
    path('employer/jobs/', views.EmployerJobsAPI.as_view(), name='employer_jobs'),
    
    # ViewSet endpoints with advanced features
    path('api/v2/', include(router.urls)),
]