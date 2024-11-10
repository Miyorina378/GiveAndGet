from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users_app.models import GGUser

# Register your models here.

@admin.register(GGUser)
class GGUserAdmin(admin.ModelAdmin):
    list_display = [
        'username', 'email', 'is_staff', 'is_active', 
        'date_joined', 'profile_picture', 'user_id', 'status', 'last_login']
    search_fields = ['username', 'email']
    list_filter = ['status']
    exclude = [ 'groups', 'user_permissions']

