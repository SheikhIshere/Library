from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

GENDER_CHOICES = {
    'm': 'Male',
    'f': 'Female',
    'o': 'Other',
}

class ProfileModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to="profiles/", blank=True, null=True)  # profile picture
    name = models.CharField(max_length=100, blank=True)
    age = models.IntegerField(blank=True, null=True)
    balance = models.IntegerField(default=0)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=10, default='o')
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    social_link = models.URLField(blank=True)
    is_varified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"


# Auto-create profile when a new user is created
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        ProfileModel.objects.create(user=instance)
    else:
        # ensure profile exists
        ProfileModel.objects.get_or_create(user=instance)
        instance.profile.save()
