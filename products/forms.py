from django import forms
from .models import Product
from users_app.models import Report

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image']  # เพิ่ม image

