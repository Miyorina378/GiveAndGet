from django.urls import path
from products import views as product_views

urlpatterns = [
    path('', product_views.product_list, name='product_list'),
    path('add/', product_views.add_product, name='add_product'),
    path('delete/<int:product_id>/', product_views.delete_product, name='delete_product'),
    path('edit/<int:product_id>/', product_views.edit_product, name='edit_product'),
    path('<int:product_id>/', product_views.product_detail, name='product_detail'),
    path('add_report/', product_views.add_report, name='add_report'),

]

