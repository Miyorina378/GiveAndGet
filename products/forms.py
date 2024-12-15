from django import forms
from .models import Product
from users_app.models import Report

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image']  # เพิ่ม image
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            raise forms.ValidationError("กรุณาอัปโหลดรูปภาพสินค้าก่อนที่จะเพิ่มสินค้า.")
        return image
