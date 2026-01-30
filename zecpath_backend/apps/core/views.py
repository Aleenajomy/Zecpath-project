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
from .models import Job, CustomUser, Application, Employer, Candidate
from .serializers import JobSerializer, UserSerializer, SignupSerializer, ApplicationSerializer, CandidateProfileSerializer, EmployerProfileSerializer, ResumeUploadSerializer
from .permissions import IsAdmin, IsEmployer, IsCandidate, IsOwnerOrAdmin
from .exceptions import APIResponse
import os

@api_view(['GET'])
@permission_classes([AllowAny])
def home_api(request):
    return APIResponse.success({"message": "Hello Zecpath Backend"}, "API is running")

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user = CustomUser.objects.create_user(
            email=serializer.validated_data['email'],
            username=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            role=serializer.validated_data['role'],
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name']
        )
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
    return APIResponse.error("Registration failed", serializer.errors)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
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

@api_view(['POST'])
def logout(request):
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return APIResponse.error('Refresh token required')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return APIResponse.success(message='Logout successful')
    except TokenError:
        return APIResponse.error('Invalid token')

class JobListAPI(APIView):
    def get(self, request):
        jobs = Job.objects.all().order_by('-created_at')
        
        # Add pagination
        page_size = int(request.GET.get('page_size', 10))
        page_number = int(request.GET.get('page', 1))
        
        paginator = Paginator(jobs, page_size)
        page_obj = paginator.get_page(page_number)
        
        serializer = JobSerializer(page_obj, many=True)
        
        return Response({
            'count': paginator.count,
            'next': f"?page={page_obj.next_page_number()}&page_size={page_size}" if page_obj.has_next() else None,
            'previous': f"?page={page_obj.previous_page_number()}&page_size={page_size}" if page_obj.has_previous() else None,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'results': serializer.data
        }, status=status.HTTP_200_OK)

class JobCreateAPI(APIView):
    permission_classes = [IsEmployer]
    
    def post(self, request):
        try:
            employer = Employer.objects.get(user=request.user)
            serializer = JobSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(employer=employer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Employer.DoesNotExist:
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
        
        # Add pagination
        page_size = int(request.GET.get('page_size', 10))
        page_number = int(request.GET.get('page', 1))
        
        paginator = Paginator(users, page_size)
        page_obj = paginator.get_page(page_number)
        
        serializer = UserSerializer(page_obj, many=True)
        
        return Response({
            'count': paginator.count,
            'next': f"?page={page_obj.next_page_number()}&page_size={page_size}" if page_obj.has_next() else None,
            'previous': f"?page={page_obj.previous_page_number()}&page_size={page_size}" if page_obj.has_previous() else None,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'results': serializer.data
        }, status=status.HTTP_200_OK)

class JobApplicationAPI(APIView):
    permission_classes = [IsCandidate]
    
    def post(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id)
            candidate = request.user.candidate
            
            # Check if already applied
            if Application.objects.filter(candidate=candidate, job=job).exists():
                return Response({'error': 'Already applied to this job'}, status=status.HTTP_400_BAD_REQUEST)
            
            application = Application.objects.create(candidate=candidate, job=job)
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
    permission_classes = [IsEmployer]
    
    def get(self, request):
        try:
            employer = Employer.objects.get(user=request.user)
            jobs = Job.objects.filter(employer=employer).order_by('-created_at')
            
            # Add pagination
            page_size = int(request.GET.get('page_size', 10))
            page_number = int(request.GET.get('page', 1))
            
            paginator = Paginator(jobs, page_size)
            page_obj = paginator.get_page(page_number)
            
            serializer = JobSerializer(page_obj, many=True)
            
            return Response({
                'count': paginator.count,
                'next': f"?page={page_obj.next_page_number()}&page_size={page_size}" if page_obj.has_next() else None,
                'previous': f"?page={page_obj.previous_page_number()}&page_size={page_size}" if page_obj.has_previous() else None,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'current_page': page_obj.number,
                'results': serializer.data
            })
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
        try:
            candidate = Candidate.objects.get(user=request.user)
            serializer = ResumeUploadSerializer(candidate, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Resume uploaded successfully',
                    'resume_url': request.build_absolute_uri(candidate.resume.url) if candidate.resume else None
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate profile not found'}, status=status.HTTP_400_BAD_REQUEST)

class ResumeDeleteAPI(APIView):
    permission_classes = [IsCandidate]
    
    def delete(self, request):
        try:
            candidate = Candidate.objects.get(user=request.user)
            if candidate.resume:
                if os.path.exists(candidate.resume.path):
                    os.remove(candidate.resume.path)
                candidate.resume = None
                candidate.save()
                return Response({'message': 'Resume deleted successfully'})
            return Response({'error': 'No resume found'}, status=status.HTTP_404_NOT_FOUND)
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate profile not found'}, status=status.HTTP_400_BAD_REQUEST)

class ResumeDownloadAPI(APIView):
    permission_classes = [IsCandidate | IsEmployer | IsAdmin]
    
    def get(self, request, candidate_id=None):
        try:
            if request.user.role == 'candidate':
                candidate = Candidate.objects.get(user=request.user)
            else:
                if not candidate_id:
                    return Response({'error': 'Candidate ID required'}, status=status.HTTP_400_BAD_REQUEST)
                candidate = Candidate.objects.get(id=candidate_id)
            
            if not candidate.resume:
                return Response({'error': 'No resume found'}, status=status.HTTP_404_NOT_FOUND)
            
            if not os.path.exists(candidate.resume.path):
                return Response({'error': 'Resume file not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get file extension to set proper content type
            ext = os.path.splitext(candidate.resume.name)[1].lower()
            content_type = {
                '.pdf': 'application/pdf',
                '.doc': 'application/msword',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }.get(ext, 'application/octet-stream')
            
            with open(candidate.resume.path, 'rb') as f:
                response = HttpResponse(f.read(), content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(candidate.resume.name)}"'
                return response
                
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)