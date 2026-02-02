from django.contrib import admin
from .models import Candidate

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['user', 'experience_years', 'expected_salary']
    list_filter = ['experience_years', 'expected_salary']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']