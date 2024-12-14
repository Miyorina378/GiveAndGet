from django.db import models
from django.conf import settings
from products.models import Product

class Chat(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_chats')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_chats')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    last_read = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)  # For notification

    def __str__(self):
        return f"{self.sender} to {self.receiver} at {self.timestamp}"

    @staticmethod
    def get_unread_count(user):
        # คำนวณจำนวนข้อความที่ยังไม่ได้อ่าน
        unread_count = Chat.objects.filter(
            receiver=user, is_read=False
        ).exclude(
            sender=user  # ไม่รวมข้อความที่ผู้ใช้ส่งเอง
        ).count()
        return unread_count

    def mark_as_read(self):
        # อัพเดตสถานะการอ่านเมื่อผู้ใช้คลิกเปิดห้องแชท
        self.is_read = True
        self.last_read = self.timestamp
        self.save()


class TradeRequest(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trade_requests_sent")
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trade_requests_received")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50)  # Example: "money" or "items"
    location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default="pending")  # Example: "pending", "accepted", "declined"

    def __str__(self):
        return f"TradeRequest: {self.buyer} -> {self.seller} ({self.product})"




