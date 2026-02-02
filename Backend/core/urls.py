from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('', views.home_api, name='home_api'),
    
    # Auth endpoints
    path('auth/signup/', views.signup, name='signup'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Public job listing endpoints
    path('jobs/', views.JobListAPI.as_view(), name='job_list'),
    path('jobs/featured/', views.FeaturedJobsAPI.as_view(), name='featured_jobs'),
    path('jobs/latest/', views.LatestJobsAPI.as_view(), name='latest_jobs'),
    path('jobs/<int:job_id>/apply/', views.JobApplicationAPI.as_view(), name='job_apply'),
    
    # Application tracking endpoints
    path('applications/', views.ApplicationListAPI.as_view(), name='application_list'),
    path('applications/<int:app_id>/', views.ApplicationDetailAPI.as_view(), name='application_detail'),
    path('applications/<int:app_id>/status/', views.ApplicationStatusUpdateAPI.as_view(), name='application_status_update'),
    
    # Admin endpoints
    path('admin/dashboard/', views.AdminDashboardAPI.as_view(), name='admin_dashboard'),
    path('profile/', views.UserTestAPI.as_view(), name='user_profile'),
    
    # Include app-specific URLs
    path('candidates/', include('candidates.urls')),
    path('employers/', include('employers.urls')),
]