from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Employer, Candidate

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'employer':
            Employer.objects.create(user=instance)
        elif instance.role == 'candidate':
            Candidate.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'employer' and hasattr(instance, 'employer'):
        instance.employer.save()
    elif instance.role == 'candidate' and hasattr(instance, 'candidate'):
        instance.candidate.save()