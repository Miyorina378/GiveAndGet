from django.urls import path
from . import views

urlpatterns = [
    path('add-meet/', views.add_meeting_point, name='add_meeting_point'),
    path('list/', views.meeting_point_list, name='meeting_point_list'),
    path('<int:id>/', views.meeting_point_detail, name='meeting_point_detail'),
    path('delete-meeting/<int:id>/', views.delete_meeting, name='delete_meeting'),
]

