import django_filters
from django.db import models
from django_filters import rest_framework as filters
from apps.core.models import CustomUser, Job, Application, Candidate, Employer

class UserFilter(filters.FilterSet):
    role = filters.ChoiceFilter(choices=CustomUser.ROLE_CHOICES)
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    is_verified = filters.BooleanFilter()
    
    class Meta:
        model = CustomUser
        fields = ['role', 'is_verified']

class JobFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=Job.STATUS_CHOICES)
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    location = filters.CharFilter(lookup_expr='icontains')
    title = filters.CharFilter(lookup_expr='icontains')
    company = filters.CharFilter(field_name='employer__company_name', lookup_expr='icontains')
    
    class Meta:
        model = Job
        fields = ['status', 'location']

class ApplicationFilter(filters.FilterSet):
    status = filters.CharFilter(lookup_expr='icontains')
    applied_after = filters.DateTimeFilter(field_name='applied_at', lookup_expr='gte')
    applied_before = filters.DateTimeFilter(field_name='applied_at', lookup_expr='lte')
    job_title = filters.CharFilter(field_name='job__title', lookup_expr='icontains')
    candidate_email = filters.CharFilter(field_name='candidate__user__email', lookup_expr='icontains')
    
    class Meta:
        model = Application
        fields = ['status']

class CandidateFilter(filters.FilterSet):
    experience_years_min = filters.NumberFilter(field_name='experience_years', lookup_expr='gte')
    experience_years_max = filters.NumberFilter(field_name='experience_years', lookup_expr='lte')
    expected_salary_min = filters.NumberFilter(field_name='expected_salary', lookup_expr='gte')
    expected_salary_max = filters.NumberFilter(field_name='expected_salary', lookup_expr='lte')
    has_resume = filters.BooleanFilter(field_name='resume', lookup_expr='isnull', exclude=True)
    
    class Meta:
        model = Candidate
        fields = []

class EmployerFilter(filters.FilterSet):
    verification = filters.BooleanFilter()
    company_size = filters.CharFilter(lookup_expr='icontains')
    domain = filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Employer
        fields = ['verification']