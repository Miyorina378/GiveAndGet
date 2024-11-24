# users_app/urls.py
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', view=views.register, name='register'),
    path('dashboard/', view=views.dashboard, name='dashboard'),
    path('', include("django.contrib.auth.urls")),
    path('chat/', include('chat_app.urls')),
    path('update-username/', views.update_username, name='update_username'),
    path('update-email/', views.update_email, name='update_email'),
    path('update-profile-picture/', views.update_profile_picture, name='update_profile_picture'),
    path('submit-report/', views.submit_report, name='submit_report'),
]
