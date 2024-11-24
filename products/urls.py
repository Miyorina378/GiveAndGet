from django.urls import path
from products import views as product_views
from users_app import views as user_views

urlpatterns = [
    path('', product_views.product_list, name='product_list'),
    path('add/', product_views.add_product, name='add_product'),
    path('delete/<int:product_id>/', product_views.delete_product, name='delete_product'),
    path('edit/<int:product_id>/', product_views.edit_product, name='edit_product'),
    path('users/<str:username>/report/', user_views.report_user, name='report_user'), 
    path('<int:product_id>/', product_views.product_detail, name='product_detail'),
]

