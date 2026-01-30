from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Employer, Candidate, Job, Application

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['email', 'role', 'first_name', 'last_name', 'password', 'confirm_password']
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'role', 'is_verified', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }
    
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = ['company_name', 'website', 'domain', 'company_description', 'company_size', 'verification']

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['skills', 'education', 'experience', 'expected_salary', 'experience_years', 'resume']

class ResumeUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['resume']
    
    def validate_resume(self, value):
        if not value:
            raise serializers.ValidationError("Resume file is required")
        return value

class EmployerProfileSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Employer
        fields = ['company_name', 'website', 'domain', 'company_description', 'company_size', 'verification', 'user_info']
    
    def get_user_info(self, obj):
        return {
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name
        }

class CandidateProfileSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()
    resume_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Candidate
        fields = ['skills', 'education', 'experience', 'expected_salary', 'experience_years', 'resume', 'resume_url', 'user_info']
    
    def get_user_info(self, obj):
        return {
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name
        }
    
    def get_resume_url(self, obj):
        if obj.resume:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.resume.url)
        return None

class JobSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    publisher_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'location', 'status', 'created_at', 'company_name', 'publisher_name']
        read_only_fields = ['id', 'created_at', 'company_name', 'publisher_name']
    
    def get_company_name(self, obj):
        return obj.employer.company_name
    
    def get_publisher_name(self, obj):
        return f"{obj.employer.user.first_name} {obj.employer.user.last_name}".strip()

class ApplicationSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.user.email', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    
    class Meta:
        model = Application
        fields = '__all__'