from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .forms import ProductForm
from django.contrib.auth.decorators import login_required

@login_required
def product_list(request):
    products = Product.objects.filter(user=request.user)  # แสดงสินค้าของผู้ใช้ที่ล็อกอินอยู่
    return render(request, 'products/product_list.html', {'products': products})



@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user  # กำหนด user ที่เพิ่มสินค้า
            product.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {'form': form})

def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('product_list')  # กลับไปที่หน้ารายการสินค้า

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # ค้นหาสินค้าตาม ID
    return render(request, 'products/product_detail.html', {'product': product})
