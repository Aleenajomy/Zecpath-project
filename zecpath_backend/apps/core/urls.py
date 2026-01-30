from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
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
    path('', views.home_api, name='home_api'),
    
    # Auth endpoints
    path('auth/signup/', views.signup, name='signup'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API endpoints with advanced features
    path('api/', include(router.urls)),
    
    # Resume endpoints
    path('api/resume/upload/', views.ResumeUploadAPI.as_view(), name='resume_upload'),
    path('api/resume/delete/', views.ResumeDeleteAPI.as_view(), name='resume_delete'),
    path('api/resume/download/', views.ResumeDownloadAPI.as_view(), name='resume_download'),
    path('api/resume/download/<int:candidate_id>/', views.ResumeDownloadAPI.as_view(), name='resume_download_by_id'),
    
    # Admin endpoints
    path('api/admin/dashboard/', views.AdminDashboardAPI.as_view(), name='admin_dashboard'),
]