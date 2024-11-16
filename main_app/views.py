from django.shortcuts import render
from django.http import HttpResponse
from products.models import Product

# Create your views here.
def home(request):
    products = Product.objects.all()  # ดึงสินค้าทั้งหมดจากฐานข้อมูล
    return render(request, 'main_app/home.html', {'products': products})


def about(request):
    return render(request, 'main_app/about.html')

