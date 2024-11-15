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
]
