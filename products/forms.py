from django import forms
from .models import Product
from users_app.models import Report

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image']  # เพิ่ม image


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'report_description']
        widgets = {
            'report_description': forms.Textarea(attrs={'placeholder': 'Describe the issue...'}),
        }
