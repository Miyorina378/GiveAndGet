from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .forms import ProductForm
from users_app.models import Report
from users_app.forms import ReportForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.apps import apps


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
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products/product_detail.html', {
        'product': product,
        'added_by': product.user.username,  # ส่งชื่อผู้เพิ่มสินค้าไปยังเทมเพลต
    })


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)  # ตรวจสอบว่าเป็นสินค้าของผู้ใช้
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/add_product.html', {'form': form, 'is_edit': True})

@login_required
def add_report(request, reported_user_id):
    print("Reported User ID:", reported_user_id)

    reported_user = get_object_or_404(Product, id=reported_user_id)

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user  # Set the reporter to the current user
            report.reported_user = reported_user  # Assign the reported user
            report.save()

            # Redirect to the product detail page (replace 'product_detail' with your view name)
        return redirect('products/product_detail.html', pk=request.POST.get('product_id'))
    else:
        form = ReportForm()

    return render(request, 'products/product_detail.html', {'form': form})
