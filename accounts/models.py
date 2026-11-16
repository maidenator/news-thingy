from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user model for News Thingy.
    Inherits from AbstractUser to provide standard username, email, password,
    while ensuring email is unique and ready for future newsletter subscriptions.
    """
    email = models.EmailField(unique=True, blank=False, verbose_name="Email Address")

    def __str__(self):
        return self.username

