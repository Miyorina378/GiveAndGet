from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.conf import settings
from products.models import Product

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
    
class Report(models.Model):
    REASON_CHOICES = [
        ('User is spamming or harassment', 'User is spamming or harassment'),
        ('This user is a bot', 'This user is a bot'),
        ('This Product is not delivered on time', 'This Product is not delivered on time'),
        ('Posting copyrighted product', 'Posting copyrighted product'),
        ('Posting illegal product', 'Posting illegal product'),
    ]
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_report_sender')
    reported_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_reported_user')
    reason = models.CharField(max_length=60, choices=REASON_CHOICES)
    report_description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Reviewed', 'Reviewed'),
            ('Resolved', 'Resolved'),
            ('Dismissed', 'Dismissed'),
        ],
        default='Pending',
    )
    date_filed = models.DateTimeField(auto_now_add=True)
    action_taken = models.TextField(blank=True, null=True)

    def __str__(self):
        # Ensure the reported_product exists before trying to access its name
        return f'Report by {self.reporter} on {self.reported_user} for {self.reason}'


    
    
