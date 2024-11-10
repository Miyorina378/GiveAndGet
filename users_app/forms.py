from django.contrib.auth.forms import UserCreationForm
from users_app.models import GGUser
class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = GGUser
        fields = UserCreationForm.Meta.fields + ("email", )