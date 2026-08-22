from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    if created:
        StudentProfile.objects.create(user=instance)


class StudentProfile(models.Model):
    LEVELS = (
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.CharField(max_length=10, choices=LEVELS)
    coins = models.IntegerField(default=100)
    savings = models.FloatField(default=0)
    happiness = models.IntegerField(default=50)

    def __str__(self):
        return self.user.username


class GameHistory(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    action = models.CharField(max_length=10)
    amount = models.IntegerField()
    result = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)