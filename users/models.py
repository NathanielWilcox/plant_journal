from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Custom User model extending AbstractUser to allow future customizations."""
    # custom fields
    display_name = models.CharField(max_length=150, blank=True, null=True, help_text="Alias shown in the app (defaults to username)")
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # Meta class
    class Meta:
        ordering = ['username']

    # String representation
    def __str__(self):
        return self.username