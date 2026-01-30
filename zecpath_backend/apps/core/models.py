from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
from django.db import models
import os
from utils.file_validators import FileValidator, resume_upload_path

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('employer', 'Employer'),
        ('candidate', 'Candidate'),
    ]
    
    email = models.EmailField(unique=True)
    # phone = models.CharField(max_length=15, blank=True, unique=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, db_index=True)
    is_verified = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']
    
    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt', 'argon2')):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.email

class Employer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200, blank=True, db_index=True)
    website = models.URLField(blank=True)
    domain = models.CharField(max_length=100, blank=True, db_index=True)
    company_description = models.TextField(blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    verification = models.BooleanField(default=False, db_index=True)
    
    def __str__(self):
        return self.company_name or self.user.email

class Candidate(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    skills = models.JSONField(default=dict, blank=True)
    education = models.CharField(max_length=200, blank=True)
    experience = models.CharField(max_length=500, blank=True)
    expected_salary = models.IntegerField(null=True, blank=True, db_index=True)
    experience_years = models.IntegerField(default=0, db_index=True)
    resume = models.FileField(
        upload_to=resume_upload_path,
        validators=[FileValidator()],
        blank=True,
        null=True
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['experience_years', 'expected_salary']),
        ]
    
    def save(self, *args, **kwargs):
        # Delete old resume when uploading new one
        if self.pk:
            try:
                old_resume = Candidate.objects.get(pk=self.pk).resume
                if old_resume and old_resume != self.resume:
                    if os.path.isfile(old_resume.path):
                        os.remove(old_resume.path)
            except (Candidate.DoesNotExist, OSError, ValueError):
                pass  # Continue even if old file deletion fails
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.email

class Job(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
    ]
    
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    location = models.CharField(max_length=100, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['location', 'status']),
            models.Index(fields=['title', 'status']),
        ]
    
    def __str__(self):
        return self.title

class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', db_index=True)
    applied_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'applied_at']),
            models.Index(fields=['candidate', 'applied_at']),
            models.Index(fields=['job', 'applied_at']),
        ]
        unique_together = ['candidate', 'job']
    
    def __str__(self):
        return f"{self.candidate.user.email} - {self.job.title}"