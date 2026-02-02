from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.permissions import IsCandidate, IsAdmin
from .models import Candidate
from .serializers import CandidateProfileSerializer, ResumeUploadSerializer
from .services import CandidateService
from core.exceptions import APIResponse

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
        candidate, error = CandidateService.update_candidate_profile(request.user, request.data)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CandidateProfileSerializer(candidate, context={'request': request})
        return Response(serializer.data)
    
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

class ResumeUploadAPI(APIView):
    permission_classes = [IsCandidate]
    
    def post(self, request):
        file = request.FILES.get('resume')
        candidate, error = CandidateService.upload_resume(request.user, file)
        
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': 'Resume uploaded successfully',
            'resume_url': request.build_absolute_uri(candidate.resume.url) if candidate.resume else None
        }, status=status.HTTP_200_OK)

class ResumeDeleteAPI(APIView):
    permission_classes = [IsCandidate]
    
    def delete(self, request):
        success, message = CandidateService.delete_resume(request.user)
        
        if success:
            return Response({'message': message})
        return Response({'error': message}, status=status.HTTP_404_NOT_FOUND)

class ResumeDownloadAPI(APIView):
    permission_classes = [IsCandidate | IsAdmin]
    
    def get(self, request, candidate_id=None):
        response, error = CandidateService.download_resume(request.user, candidate_id)
        
        if error:
            return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)
        
        return response