from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    
    # TODO: Add:
    #
    # - password_changed_at
    # - last_login_at
    # - reset_requested_at
    # - reset_completed_at
    
    # Optional:
    #
    # - is_ban
    # - activated_at
    # - is_mfa_enabled
    # - mfa_secret_changed_at
    # - mfa_reset_at
    # - ...
    
    
    def __str__(self):
        return self.username
