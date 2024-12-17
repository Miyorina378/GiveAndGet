from django import forms
from .models import MeetingPoint

class MeetingPointForm(forms.ModelForm):
    class Meta:
        model = MeetingPoint
        fields = ['product_name', 'payment_method', 'pickup_location', 'meeting_date', 'meeting_time', 'seller_name']
        widgets = {
            'meeting_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'meeting_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_method': forms.TextInput(attrs={'class': 'form-control'}),
            'pickup_location': forms.TextInput(attrs={'class': 'form-control'}),
            'seller_name': forms.TextInput(attrs={'class': 'form-control'}),
        }