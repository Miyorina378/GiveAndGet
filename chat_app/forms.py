from django import forms
from .models import Chat
from django.contrib.auth import get_user_model

User = get_user_model()
class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'placeholder': 'Type your message...', 'rows': 4, 'cols': 40}),
        }

class UserSearchForm(forms.Form):
    username = forms.CharField(max_length=150, required=False, label='Search by username')

