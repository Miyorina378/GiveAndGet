from django import forms
from .models import Product
from users_app.models import Report

class ProductForm(forms.ModelForm):
    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('books', 'Books'),
        ('clothing&fashion', 'Clothing & Fashion'),
        ('home&living', 'Home & Living'),
        ('tools&equipment', 'Tools & Equipment'),
        ('collectibles', 'Collectibles'),
        ('health&beauty', 'Health & Beauty'),
        ('other', 'Other'),
    ]
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=False)

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'category', 'image']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            raise forms.ValidationError("กรุณาอัปโหลดรูปภาพสินค้าก่อนที่จะเพิ่มสินค้า.")
        return image
