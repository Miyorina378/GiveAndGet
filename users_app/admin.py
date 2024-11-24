from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users_app.models import GGUser, Report

# Register your models here.

@admin.register(GGUser)
class GGUserAdmin(admin.ModelAdmin):
    list_display = [
        'username', 'email', 'is_staff', 'is_active', 
        'date_joined', 'profile_picture', 'user_id', 'status', 'last_login', ]
    search_fields = ['username', 'email']
    list_filter = ['status']
    exclude = [ 'groups', 'user_permissions']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'reported_user', 'reason', 'status', 'date_filed')
    list_filter = ('status', 'reason')
    search_fields = ('reporter__username', 'reported_user__username', 'reason', 'report_description')

