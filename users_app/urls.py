# users_app/urls.py
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', view=views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', include("django.contrib.auth.urls")),
    path('chat/', include('chat_app.urls')),
    path('update-username/', views.update_username, name='update_username'),
    path('update-email/', views.update_email, name='update_email'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('update-profile-picture/', views.update_profile_picture, name='update_profile_picture'),
]
