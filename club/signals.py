# club/signals.py
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ParentProfile, SchoolProfile, StudentProfile, TeacherProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        user_type = getattr(instance, "user_type", None)
        if user_type == "parent":
            ParentProfile.objects.create(user=instance)
        elif user_type == "student":
            StudentProfile.objects.create(user=instance)
        elif user_type == "teacher":
            TeacherProfile.objects.create(user=instance)
        elif user_type == "school":
            SchoolProfile.objects.create(user=instance)