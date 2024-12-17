from django.db import models

class MeetingPoint(models.Model):
    product_name = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=50)
    pickup_location = models.CharField(max_length=100)
    meeting_date = models.DateField()
    meeting_time = models.TimeField()
    seller_name = models.CharField(max_length=100, default="")  # เพิ่มฟิลด์ชื่อผู้ขาย
    
    def __str__(self):
        return self.product_name