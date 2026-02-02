from django.urls import path
from . import views

app_name = 'candidates'

urlpatterns = [
    # Candidate profile endpoints
    path('profile/', views.CandidateProfileAPI.as_view(), name='candidate_profile'),
    
    # Resume endpoints
    path('resume/upload/', views.ResumeUploadAPI.as_view(), name='resume_upload'),
    path('resume/delete/', views.ResumeDeleteAPI.as_view(), name='resume_delete'),
    path('resume/download/', views.ResumeDownloadAPI.as_view(), name='resume_download'),
    path('resume/download/<int:candidate_id>/', views.ResumeDownloadAPI.as_view(), name='resume_download_by_id'),
]