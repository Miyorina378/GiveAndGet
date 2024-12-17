from django.urls import path
from . import views

urlpatterns = [
    path('<str:room_name>/', views.chat_room, name='chat_room'),
    path('get-user-products/<str:room_name>/', views.get_user_products, name='get_user_products'),
    path('send_trade_request/', views.send_trade_request, name='send_trade_request'),

]









