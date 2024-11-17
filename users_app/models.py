from django.db import models
from django.contrib.auth.models import AbstractUser

class GGUser(AbstractUser):
    # Adding custom fields
    profile_picture = models.ImageField(default= 'media/profile_pics/default.png', upload_to='media/profile_pics/', null=True, blank=True)
    user_id = models.PositiveIntegerField(unique=True, editable=False)
    status_choices = [
        ('online', 'Online'),
        ('busy', 'Busy'),
        ('afk', 'AFK'),
        ('offline', 'Offline'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='offline')
    last_login = models.DateTimeField(auto_now=True)
    
    # Automatically set the user_id
    def save(self, *args, **kwargs):
        if not self.user_id:
            last_user = GGUser.objects.last()
            self.user_id = (last_user.user_id + 1) if last_user else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.username} - {self.status}'
