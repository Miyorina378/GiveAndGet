from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .forms import ProductForm
from users_app.models import Report
from users_app.forms import ReportForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
import os



User = get_user_model()

@login_required
def product_list(request):
    # รับค่าหมวดหมู่จาก URL (ถ้ามี)
    category_filter = request.GET.get('category', None)
    
    # กรองสินค้าตามหมวดหมู่
    if category_filter:
        products = Product.objects.filter(user=request.user, category=category_filter)
    else:
        products = Product.objects.filter(user=request.user)
    
    return render(request, 'products/product_list.html', {'products': products, 'category_filter': category_filter})

@login_required
def add_product(request, product_id=None):
    if product_id:
        is_edit = True
        product = Product.objects.get(id=product_id)
        form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    else:
        is_edit = False
        form = ProductForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        # ตรวจสอบว่ามีการอัปโหลดไฟล์รูปภาพหรือไม่
        if not request.FILES.get('image'):
            messages.error(request, 'กรุณาอัปโหลดรูปภาพสินค้าก่อนที่จะเพิ่มสินค้า.')
            return render(request, 'products/add_product.html', {'form': form, 'is_edit': is_edit})

        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user  # กำหนด user ที่เพิ่มสินค้า
            product.save()
            return redirect('product_list')

    return render(request, 'products/add_product.html', {'form': form, 'is_edit': is_edit})

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
    old_image = product.image  # เก็บไฟล์รูปภาพเดิมไว้

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            # ตรวจสอบและลบรูปภาพเดิมหากมีการอัพโหลดรูปภาพใหม่
            if 'image' in request.FILES:
                if old_image and os.path.isfile(old_image.path):  # ถ้ามีไฟล์เก่าและไฟล์นั้นมีอยู่จริง
                    os.remove(old_image.path)  # ลบไฟล์เก่า
            form.save()  # บันทึกข้อมูลใหม่
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/add_product.html', {'form': form, 'is_edit': True})

@login_required
def add_report(request):
    if request.method == 'POST':
        reported_user_username = request.POST.get('reported_user_username')  # Get username from hidden input
        reason = request.POST.get('reason')
        description = request.POST.get('description')

        # Check if the reported user exists
        try:
            reported_user = User.objects.get(username=reported_user_username)
        except User.DoesNotExist:
            return HttpResponse(f"ERROR: Reported user with username '{reported_user_username}' does not exist.")

        # Create and save the report
        report = Report(
            reporter=request.user,
            reported_user=reported_user,
            reason=reason,
            report_description=description,
        )
        report.save()

        # Redirect back to the referring page or a default page
        return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))

    # For GET requests, return a form or redirect to the main page
    return redirect('products:product_list')





