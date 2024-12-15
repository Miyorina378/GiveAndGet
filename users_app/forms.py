from django.contrib.auth.forms import UserCreationForm
from users_app.models import GGUser
from django import forms
from .models import Report

class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = GGUser
        fields = UserCreationForm.Meta.fields + ("email", )

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = GGUser
        fields = ['profile_picture']

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'report_description']  # Fields to be filled by the reporter
        widgets = {
            'reason': forms.Select(
                attrs={
                    'class': 'form-select',  # Bootstrap's dropdown styling
                    'id': 'reportReason',  # Matches the label's for attribute
                }
            ),
            'report_description': forms.Textarea(
                attrs={
                    'class': 'form-control',  # Bootstrap's textarea styling
                    'id': 'reportDescription',  # Matches the label's for attribute
                    'rows': 4,
                }
            ),
        }