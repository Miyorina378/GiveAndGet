# chat_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('chat/<int:user_id>/', views.chat_room, name='chat_room'),  # Specific chat room
]


