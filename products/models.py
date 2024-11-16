from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# Signal to delete image file when Product is deleted
@receiver(post_delete, sender=Product)
def delete_product_image(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):  # ตรวจสอบว่าไฟล์มีอยู่จริง
            os.remove(instance.image.path)  # ลบไฟล์
