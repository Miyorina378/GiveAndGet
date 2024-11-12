from django.db import models
from django.conf import settings

class Chat(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_chats')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_chats')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    last_read = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.sender} to {self.receiver} at {self.timestamp}"

