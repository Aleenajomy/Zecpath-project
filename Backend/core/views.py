from django.http import JsonResponse, HttpResponse, Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.exceptions import ValidationError
from .models import CustomUser, Application
from employers.models import Job, Employer
from candidates.models import Candidate
from .serializers import UserSerializer, SignupSerializer, ApplicationSerializer
from employers.serializers import JobSerializer, EmployerProfileSerializer
from candidates.serializers import CandidateProfileSerializer, ResumeUploadSerializer
from .permissions import IsAdmin, IsEmployer, IsCandidate, IsOwnerOrAdmin
from .exceptions import APIResponse
from common.utils.pagination import paginate_queryset
from common.utils.filters import JobFilter
from common.utils.search import JobSearchMixin
from common.utils.pagination import InfiniteScrollPagination

# Import services with error handling
try:
    from common.services.auth_service import AuthService
    from common.services.job_service import JobService
    from common.services.file_service import FileService
except ImportError:
    # Fallback if services not available
    AuthService = None
    JobService = None
    FileService = None

@api_view(['GET'])
@permission_classes([AllowAny])
def home_api(request):
    return APIResponse.success({"message": "Hello Zecpath Backend"}, "API is running")

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    try:
        # Debug: Print request data
        print(f"Signup request data: {request.data}")
        
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = CustomUser.objects.create_user(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                role=serializer.validated_data['role'],
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name']
            )
            
            # Profile creation is handled by signals automatically
            
            refresh = RefreshToken.for_user(user)
            data = {
                'user': {
                    'email': user.email,
                    'role': user.role,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                },
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return APIResponse.created(data, "User registered successfully")
        else:
            # Debug: Print validation errors
            print(f"Validation errors: {serializer.errors}")
            return APIResponse.error("Registration failed", serializer.errors)
    except Exception as e:
        print(f"Signup exception: {str(e)}")
        return APIResponse.error(f"Registration error: {str(e)}")

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return APIResponse.error('Email and password required')
        
        user = authenticate(username=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            data = {
                'user': {
                    'email': user.email,
                    'role': user.role,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                },
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return APIResponse.success(data, "Login successful")
        return APIResponse.unauthorized('Invalid credentials')
    except Exception as e:
        return APIResponse.error(f"Login error: {str(e)}")

@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return APIResponse.error("Refresh token required")
        
        token = RefreshToken(refresh_token)
        token.blacklist()
        return APIResponse.success(message="Logout successful")
    except TokenError:
        return APIResponse.error("Invalid token")
    except Exception as e:
        return APIResponse.error(f"Logout error: {str(e)}")

class JobListAPI(APIView, JobSearchMixin):
    permission_classes = [AllowAny]
    
    def get(self, request):
        jobs = Job.objects.filter(status='published').select_related('employer__user').prefetch_related('employer')
        
        # Apply manual filters
        jobs = self.apply_filters(jobs, request)
        
        # Apply search
        jobs = self.apply_search(jobs)
        
        # Use infinite scroll if requested
        if request.GET.get('infinite_scroll') == 'true':
            paginator = InfiniteScrollPagination()
            page = paginator.paginate_queryset(jobs, request)
            serializer = JobSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        # Standard pagination
        result = paginate_queryset(jobs, request)
        serializer = JobSerializer(result['page_obj'], many=True)
        result['results'] = serializer.data
        del result['page_obj']
        
        return Response(result, status=status.HTTP_200_OK)
    
    def apply_filters(self, queryset, request):
        """Apply manual filters"""
        params = request.GET
        
        # Skills filter
        if params.get('skills'):
            skills_list = [skill.strip() for skill in params.get('skills').split(',')]
            for skill in skills_list:
                queryset = queryset.filter(skills__icontains=skill)
        
        # Salary filters
        if params.get('salary_min'):
            queryset = queryset.filter(salary_min__gte=params.get('salary_min'))
        if params.get('salary_max'):
            queryset = queryset.filter(salary_max__lte=params.get('salary_max'))
        
        # Experience range filters (SQLite compatible)
        if params.get('experience_min'):
            try:
                min_exp = int(params.get('experience_min'))
                queryset = queryset.filter(experience__icontains=str(min_exp))
            except ValueError:
                pass
        if params.get('experience_max'):
            try:
                max_exp = int(params.get('experience_max'))
                queryset = queryset.filter(experience__icontains=str(max_exp))
            except ValueError:
                pass
        
        # Location filter
        if params.get('location'):
            queryset = queryset.filter(location__icontains=params.get('location'))
        
        # Job type filter
        if params.get('job_type'):
            queryset = queryset.filter(job_type=params.get('job_type'))
        
        # Featured filter
        if params.get('is_featured'):
            queryset = queryset.filter(is_featured=params.get('is_featured').lower() == 'true')
        
        return queryset.order_by('-is_featured', '-created_at')

class FeaturedJobsAPI(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        jobs = Job.objects.filter(status='published', is_featured=True).select_related('employer__user').order_by('-created_at')
        result = paginate_queryset(jobs, request)
        
        serializer = JobSerializer(result['page_obj'], many=True)
        result['results'] = serializer.data
        del result['page_obj']
        
        return Response(result, status=status.HTTP_200_OK)

class LatestJobsAPI(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        limit = int(request.GET.get('limit', 10))
        jobs = Job.objects.filter(status='published').select_related('employer__user').order_by('-created_at')[:limit]
        serializer = JobSerializer(jobs, many=True)
        return Response({'results': serializer.data}, status=status.HTTP_200_OK)

class JobCreateAPI(APIView):
    permission_classes = [IsEmployer]
    
    def post(self, request):
        # Debug logging
        print(f"User: {request.user}")
        print(f"Is authenticated: {request.user.is_authenticated}")
        print(f"User role: {getattr(request.user, 'role', 'No role')}")
        print(f"Authorization header: {request.META.get('HTTP_AUTHORIZATION', 'No header')}")
        
        try:
            employer = Employer.objects.get(user=request.user)
            print(f"Employer found: {employer}")
            serializer = JobSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(employer=employer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Employer.DoesNotExist:
            print("Employer profile not found")
            return Response({'error': 'Employer profile not found'}, status=status.HTTP_400_BAD_REQUEST)

class JobUpdateAPI(APIView):
    permission_classes = [IsEmployer]
    
    def put(self, request, job_id):
        try:
            employer = Employer.objects.get(user=request.user)
            job = Job.objects.get(id=job_id, employer=employer)
            serializer = JobSerializer(job, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Employer.DoesNotExist:
            return Response({'error': 'Employer profile not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found or not owned by you'}, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, job_id):
        return self.put(request, job_id)
    
    def delete(self, request, job_id):
        try:
            employer = Employer.objects.get(user=request.user)
            job = Job.objects.get(id=job_id, employer=employer)
            job.delete()
            return Response({'message': 'Job deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Employer.DoesNotExist:
            return Response({'error': 'Employer profile not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found or not owned by you'}, status=status.HTTP_404_NOT_FOUND)

class UserTestAPI(APIView):
    permission_classes = [IsAdmin]
    
    def get(self, request):
        users = CustomUser.objects.all().order_by('-created_at')
        result = paginate_queryset(users, request)
        
        serializer = UserSerializer(result['page_obj'], many=True)
        result['results'] = serializer.data
        del result['page_obj']
        
        return Response(result, status=status.HTTP_200_OK)

class JobApplicationAPI(APIView):
    permission_classes = [IsCandidate]
    
    def post(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id)
            candidate = request.user.candidate
            
            # Check if already applied
            if Application.objects.filter(candidate=candidate, job=job).exists():
                return Response({'error': 'Already applied to this job'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create application with resume snapshot
            application = Application.objects.create(candidate=candidate, job=job)
            
            # Copy resume as snapshot if exists
            if candidate.resume:
                import shutil
                from django.core.files.base import ContentFile
                
                # Read original resume
                candidate.resume.open()
                resume_content = candidate.resume.read()
                candidate.resume.close()
                
                # Create snapshot filename
                original_name = os.path.basename(candidate.resume.name)
                snapshot_name = f"app_{application.id}_{original_name}"
                
                # Save as snapshot
                application.resume_snapshot.save(
                    snapshot_name,
                    ContentFile(resume_content),
                    save=True
                )
            
            serializer = ApplicationSerializer(application)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

class AdminDashboardAPI(APIView):
    permission_classes = [IsAdmin]
    
    def get(self, request):
        stats = {
            'total_users': CustomUser.objects.count(),
            'total_jobs': Job.objects.count(),
            'total_applications': Application.objects.count(),
            'employers': CustomUser.objects.filter(role='employer').count(),
            'candidates': CustomUser.objects.filter(role='candidate').count()
        }
        return Response(stats)

class EmployerJobsAPI(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            employer = Employer.objects.get(user=request.user)
            jobs = Job.objects.filter(employer=employer).order_by('-created_at')
            result = paginate_queryset(jobs, request)
            
            serializer = JobSerializer(result['page_obj'], many=True)
            result['results'] = serializer.data
            del result['page_obj']
            
            return Response(result)
        except Employer.DoesNotExist:
            return Response({'error': 'Employer profile not found'}, status=status.HTTP_400_BAD_REQUEST)

class CandidateProfileAPI(APIView):
    permission_classes = [IsCandidate | IsAdmin]
    
    def get(self, request):
        try:
            if request.user.role == 'admin':
                candidate_id = request.GET.get('id')
                if candidate_id:
                    candidate = Candidate.objects.get(id=candidate_id)
                else:
                    return Response({'error': 'Candidate ID required for admin'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                candidate = Candidate.objects.get(user=request.user)
            serializer = CandidateProfileSerializer(candidate, context={'request': request})
            return Response(serializer.data)
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate profile not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        try:
            if request.user.role == 'admin':
                candidate_id = request.data.get('id') or request.GET.get('id')
                if candidate_id:
                    candidate = Candidate.objects.get(id=candidate_id)
                else:
                    return Response({'error': 'Candidate ID required for admin'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                candidate = Candidate.objects.get(user=request.user)
            serializer = CandidateProfileSerializer(candidate, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate profile not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        return self.put(request)
    
    def delete(self, request):
        try:
            candidate = Candidate.objects.get(user=request.user)
            user = candidate.user
            candidate.delete()
            user.delete()
            return Response({'message': 'Profile deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate profile not found'}, status=status.HTTP_400_BAD_REQUEST)

class EmployerProfileAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def get(self, request):
        try:
            if request.user.role == 'admin':
                employer_id = request.GET.get('id')
                if employer_id:
                    employer = Employer.objects.get(id=employer_id)
                else:
                    return Response({'error': 'Employer ID required for admin'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                employer = Employer.objects.get(user=request.user)
            serializer = EmployerProfileSerializer(employer)
            return Response(serializer.data)
        except Employer.DoesNotExist:
            return Response({'error': 'Employer profile not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        try:
            if request.user.role == 'admin':
                employer_id = request.data.get('id') or request.GET.get('id')
                if employer_id:
                    employer = Employer.objects.get(id=employer_id)
                else:
                    return Response({'error': 'Employer ID required for admin'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                employer = Employer.objects.get(user=request.user)
            serializer = EmployerProfileSerializer(employer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Employer.DoesNotExist:
            return Response({'error': 'Employer profile not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        return self.put(request)
    
    def delete(self, request):
        try:
            employer = Employer.objects.get(user=request.user)
            user = employer.user
            employer.delete()
            user.delete()
            return Response({'message': 'Profile deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Employer.DoesNotExist:
            return Response({'error': 'Employer profile not found'}, status=status.HTTP_400_BAD_REQUEST)

class ResumeUploadAPI(APIView):
    permission_classes = [IsCandidate]
    
    def post(self, request):
        file = request.FILES.get('resume')
        candidate, error = FileService.upload_resume(request.user, file)
        
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': 'Resume uploaded successfully',
            'resume_url': request.build_absolute_uri(candidate.resume.url) if candidate.resume else None
        }, status=status.HTTP_200_OK)

class ResumeDeleteAPI(APIView):
    permission_classes = [IsCandidate]
    
    def delete(self, request):
        success, message = FileService.delete_resume(request.user)
        
        if success:
            return Response({'message': message})
        return Response({'error': message}, status=status.HTTP_404_NOT_FOUND)

class ResumeDownloadAPI(APIView):
    permission_classes = [IsCandidate | IsEmployer | IsAdmin]
    
    def get(self, request, candidate_id=None):
        response, error = FileService.download_resume(request.user, candidate_id)
        
        if error:
            return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)
        
        return response

class JobToggleStatusAPI(APIView):
    permission_classes = [IsEmployer]
    
    def patch(self, request, job_id):
        try:
            employer = Employer.objects.get(user=request.user)
            job = Job.objects.get(id=job_id, employer=employer)
            
            # Toggle between published and closed
            if job.status == 'published':
                job.status = 'closed'
                message = 'Job deactivated successfully'
            else:
                job.status = 'published'
                message = 'Job activated successfully'
            
            job.save()
            return Response({
                'message': message,
                'status': job.status
            })
        except (Employer.DoesNotExist, Job.DoesNotExist):
            return Response({'error': 'Job not found or not owned by you'}, status=status.HTTP_404_NOT_FOUND)

class JobActivateAPI(APIView):
    permission_classes = [IsEmployer]
    
    def post(self, request, job_id):
        try:
            employer = Employer.objects.get(user=request.user)
            job = Job.objects.get(id=job_id, employer=employer)
            job.status = 'published'
            job.save()
            return Response({'message': 'Job published successfully'})
        except (Employer.DoesNotExist, Job.DoesNotExist):
            return Response({'error': 'Job not found or not owned by you'}, status=status.HTTP_404_NOT_FOUND)

class JobDeactivateAPI(APIView):
    permission_classes = [IsEmployer]
    
    def post(self, request, job_id):
        try:
            employer = Employer.objects.get(user=request.user)
            job = Job.objects.get(id=job_id, employer=employer)
            job.status = 'closed'
            job.save()
            return Response({'message': 'Job closed successfully'})
        except (Employer.DoesNotExist, Job.DoesNotExist):
            return Response({'error': 'Job not found or not owned by you'}, status=status.HTTP_404_NOT_FOUND)

class ApplicationListAPI(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if request.user.role == 'candidate':
            applications = Application.objects.filter(candidate__user=request.user).select_related('job__employer__user').order_by('-applied_at')
        elif request.user.role == 'employer':
            applications = Application.objects.filter(job__employer__user=request.user).select_related('candidate__user', 'job').order_by('-applied_at')
            
            # Filter by ATS stage
            status_filter = request.GET.get('status')
            if status_filter:
                applications = applications.filter(status=status_filter)
            
            # Search candidates
            search = request.GET.get('search')
            if search:
                applications = applications.filter(
                    Q(candidate__user__first_name__icontains=search) |
                    Q(candidate__user__last_name__icontains=search) |
                    Q(candidate__user__email__icontains=search)
                )
                
        elif request.user.role == 'admin':
            applications = Application.objects.all().select_related('candidate__user', 'job__employer__user').order_by('-applied_at')
        else:
            return Response({'error': 'Invalid role'}, status=status.HTTP_403_FORBIDDEN)
        
        result = paginate_queryset(applications, request)
        serializer = ApplicationSerializer(result['page_obj'], many=True)
        result['results'] = serializer.data
        del result['page_obj']
        
        return Response(result)

class ApplicationDetailAPI(APIView):
    def get(self, request, app_id):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            if request.user.role == 'candidate':
                application = Application.objects.get(id=app_id, candidate__user=request.user)
            elif request.user.role == 'employer':
                application = Application.objects.get(id=app_id, job__employer__user=request.user)
            elif request.user.role == 'admin':
                application = Application.objects.get(id=app_id)
            else:
                return Response({'error': 'Invalid role'}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = ApplicationSerializer(application)
            return Response(serializer.data)
        except Application.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)

class ApplicationStatusUpdateAPI(APIView):
    def patch(self, request, app_id):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if request.user.role not in ['employer', 'admin']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            if request.user.role == 'employer':
                application = Application.objects.get(id=app_id, job__employer__user=request.user)
            else:  # admin
                application = Application.objects.get(id=app_id)
            
            new_status = request.data.get('status')
            if not new_status or new_status not in ['pending', 'reviewed', 'accepted', 'rejected']:
                return Response({'error': 'Valid status required'}, status=status.HTTP_400_BAD_REQUEST)
            
            application.status = new_status
            application.save()
            return Response({'message': 'Status updated successfully', 'status': new_status})
        except Application.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)

class JobApplicationsAPI(APIView):
    def get(self, request, job_id):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if request.user.role not in ['employer', 'admin']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            if request.user.role == 'employer':
                job = Job.objects.get(id=job_id, employer__user=request.user)
            else:  # admin
                job = Job.objects.get(id=job_id)
            
            applications = Application.objects.filter(job=job).select_related('candidate__user').order_by('-applied_at')
            
            # Filter by ATS stage
            status_filter = request.GET.get('status')
            if status_filter:
                applications = applications.filter(status=status_filter)
            
            # Search candidates
            search = request.GET.get('search')
            if search:
                applications = applications.filter(
                    Q(candidate__user__first_name__icontains=search) |
                    Q(candidate__user__last_name__icontains=search) |
                    Q(candidate__user__email__icontains=search)
                )
            
            result = paginate_queryset(applications, request)
            
            serializer = ApplicationSerializer(result['page_obj'], many=True)
            result['results'] = serializer.data
            del result['page_obj']
            
            return Response(result)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

class ShortlistCandidateAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def post(self, request, app_id):
        try:
            from utils.ats_rules import ATSWorkflowRules
            
            if request.user.role == 'employer':
                application = Application.objects.get(id=app_id, job__employer__user=request.user)
            else:
                application = Application.objects.get(id=app_id)
            
            ATSWorkflowRules.validate_transition(application.status, 'shortlisted')
            
            application._changed_by = request.user
            application.status = 'shortlisted'
            application.save()
            
            return Response({'message': 'Candidate shortlisted successfully'})
        except Application.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class RejectCandidateAPI(APIView):
    permission_classes = [IsEmployer | IsAdmin]
    
    def post(self, request, app_id):
        try:
            from utils.ats_rules import ATSWorkflowRules
            
            if request.user.role == 'employer':
                application = Application.objects.get(id=app_id, job__employer__user=request.user)
            else:
                application = Application.objects.get(id=app_id)
            
            ATSWorkflowRules.validate_transition(application.status, 'rejected')
            
            application._changed_by = request.user
            application.status = 'rejected'
            application.save()
            
            return Response({'message': 'Candidate rejected'})
        except Application.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class EmployerDashboardAPI(APIView):
    permission_classes = [IsEmployer]
    
    def get(self, request):
        try:
            employer = Employer.objects.get(user=request.user)
            
            # Get analytics data
            jobs = Job.objects.filter(employer=employer)
            applications = Application.objects.filter(job__employer=employer)
            
            # Calculate metrics
            total_jobs = jobs.count()
            total_applications = applications.count()
            shortlisted = applications.filter(status='shortlisted').count()
            selected = applications.filter(status='selected').count()
            
            # Status distribution
            status_counts = {}
            for status_choice in Application.STATUS_CHOICES:
                status = status_choice[0]
                count = applications.filter(status=status).count()
                status_counts[status] = count
            
            # Calculate ratios
            shortlist_ratio = (shortlisted / total_applications * 100) if total_applications > 0 else 0
            selection_ratio = (selected / total_applications * 100) if total_applications > 0 else 0
            
            analytics = {
                'total_jobs': total_jobs,
                'total_applications': total_applications,
                'shortlisted_count': shortlisted,
                'selected_count': selected,
                'shortlist_ratio': round(shortlist_ratio, 2),
                'selection_ratio': round(selection_ratio, 2),
                'status_distribution': status_counts
            }
            
            return Response(analytics)
        except Employer.DoesNotExist:
            return Response({'error': 'Employer profile not found'}, status=status.HTTP_400_BAD_REQUEST)