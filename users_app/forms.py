from django.contrib.auth.forms import UserCreationForm
from users_app.models import GGUser
from django import forms
from .models import Report

class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = GGUser
        fields = UserCreationForm.Meta.fields + ("email", )


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'report_description']
        widgets = {
            'report_description': forms.Textarea(attrs={'placeholder': 'Describe the issue...'}),
        }
