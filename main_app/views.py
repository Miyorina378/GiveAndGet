from django.shortcuts import render
from django.http import HttpResponse
from products.models import Product

# Create your views here.
def home(request):
    products = Product.objects.all()  # ดึงสินค้าทั้งหมดจากฐานข้อมูล
    return render(request, 'main_app/home.html', {'products': products})


def about(request):
    return render(request, 'main_app/about.html')

def home(request):
    query = request.GET.get('search', '')
    sort = request.GET.get('sort', '')
    category = request.GET.get('category', '')

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if category:
        products = products.filter(category__iexact=category)

    if sort:
        products = products.order_by(sort)

    return render(request, 'main_app/home.html', {'products': products})