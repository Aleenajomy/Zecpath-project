from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_api, name='home_api'),
    path('api/jobs/', views.JobListAPI.as_view(), name='job_list'),
    path('api/jobs/create/', views.JobCreateAPI.as_view(), name='job_create'),
    path('api/users/test/', views.UserTestAPI.as_view(), name='user_test'),
]