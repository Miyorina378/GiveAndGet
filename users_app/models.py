from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.conf import settings
from products.models import Product

class GGUser(AbstractUser):
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        null=True, 
        blank=True
    )
    user_id = models.PositiveIntegerField(unique=True, editable=False)
    first_name = models.CharField(max_length=50, blank=True)  # ชื่อ
    last_name = models.CharField(max_length=50, blank=True)   # นามสกุล
    birth_date = models.DateField(null=True, blank=True)      # วันเกิด
    phone_number = models.CharField(max_length=15, blank=True)  # เบอร์โทร
    occupation = models.CharField(max_length=100, blank=True)  # อาชีพ
    status_choices = [
        ('online', 'Online'),
        ('busy', 'Busy'),
        ('afk', 'AFK'),
        ('offline', 'Offline'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='offline')
    last_login = models.DateTimeField(auto_now=True)
    is_ban = models.BooleanField(default=False)
    ban_reason = models.TextField(null=True, blank=True)
    ban_end_date = models.DateTimeField(null=True, blank=True)

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

    