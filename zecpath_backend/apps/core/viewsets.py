from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Q, Prefetch

from .models import Job, CustomUser, Application, Employer, Candidate
from .serializers import (
    JobSerializer, UserSerializer, ApplicationSerializer, 
    CandidateProfileSerializer, EmployerProfileSerializer
)
from .permissions import IsAdmin, IsEmployer, IsCandidate
from utils.pagination import StandardPageNumberPagination, JobCursorPagination, ApplicationCursorPagination
from utils.custom_filters import CustomFilterBackend
from utils.search import JobSearchMixin, UserSearchMixin, CandidateSearchMixin, EmployerSearchMixin
from utils.querysets import OptimizedQuerysetMixin

class JobViewSet(JobSearchMixin, OptimizedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = JobSerializer
    pagination_class = StandardPageNumberPagination
    filter_backends = [CustomFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description', 'location', 'employer__company_name']
    ordering_fields = ['created_at', 'title', 'status']
    ordering = ['-created_at']
    permission_classes = []  # Allow public access for testing
    
    def filter_queryset(self, queryset):
        # Manual filtering override
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)
            
        title = self.request.query_params.get('title')
        if title:
            queryset = queryset.filter(title__icontains=title)
            
        return super().filter_queryset(queryset)
    
    def get_queryset(self):
        return Job.objects.all()
    
    def perform_create(self, serializer):
        employer = Employer.objects.get(user=self.request.user)
        serializer.save(employer=employer)
    
    @action(detail=False, methods=['get'])
    def published(self, request):
        """Get only published jobs"""
        queryset = self.get_queryset().filter(status='published')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def applications(self, request, pk=None):
        """Get applications for a specific job"""
        job = self.get_object()
        applications = OptimizedQuerysetMixin.get_optimized_applications_queryset().filter(job=job)
        page = self.paginate_queryset(applications)
        if page is not None:
            serializer = ApplicationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)

class UserViewSet(UserSearchMixin, OptimizedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = UserSerializer
    pagination_class = StandardPageNumberPagination
    filter_backends = [CustomFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'email', 'role']
    ordering = ['-created_at']
    permission_classes = [IsAdmin]
    
    def get_queryset(self):
        return CustomUser.objects.all()
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user statistics by role"""
        stats = CustomUser.objects.values('role').annotate(count=Count('id'))
        return Response(stats)

class ApplicationViewSet(OptimizedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    pagination_class = StandardPageNumberPagination  # Changed to offset-based
    filter_backends = [CustomFilterBackend, OrderingFilter]
    ordering_fields = ['applied_at', 'status']
    ordering = ['-applied_at']
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.get_optimized_applications_queryset()
        
        if user.role == 'candidate':
            return queryset.filter(candidate__user=user)
        elif user.role == 'employer':
            return queryset.filter(job__employer__user=user)
        elif user.role == 'admin':
            return queryset
        return queryset.none()
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending applications"""
        queryset = self.get_queryset().filter(status='pending')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update application status (employer/admin only)"""
        application = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        application.status = new_status
        application.save()
        serializer = self.get_serializer(application)
        return Response(serializer.data)

class CandidateViewSet(CandidateSearchMixin, OptimizedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = CandidateProfileSerializer
    pagination_class = StandardPageNumberPagination
    filter_backends = [CustomFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'education', 'experience']
    ordering_fields = ['user__created_at', 'experience_years', 'expected_salary']
    ordering = ['-user__created_at']
    permission_classes = []
    
    def get_queryset(self):
        return Candidate.objects.select_related('user')
    
    @action(detail=False, methods=['get'])
    def with_resume(self, request):
        """Get candidates with resume"""
        queryset = self.get_queryset().exclude(resume__isnull=True).exclude(resume='')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class EmployerViewSet(EmployerSearchMixin, OptimizedQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = EmployerProfileSerializer
    pagination_class = StandardPageNumberPagination
    filter_backends = [CustomFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['company_name', 'domain', 'company_description', 'user__email']
    ordering_fields = ['user__created_at', 'company_name', 'verification']
    ordering = ['-user__created_at']
    
    def get_queryset(self):
        return self.get_optimized_employers_queryset()
    
    @action(detail=False, methods=['get'])
    def verified(self, request):
        """Get verified employers"""
        queryset = self.get_queryset().filter(verification=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)