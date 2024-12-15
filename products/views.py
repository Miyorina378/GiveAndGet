from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .forms import ProductForm
from users_app.models import Report
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse



User = get_user_model()

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

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from users_app.models import Report
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()

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

    # If the request method is not POST, return an error
    return HttpResponse("ERROR: Reports can only be submitted via POST.")




