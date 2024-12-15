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

@login_required
def add_report(request):
    if request.method == 'POST':
        reported_user = User.objects.get(id=reported_user_id)
        reason = request.POST.get('reason')
        description = request.POST.get('description')

        # Create a new report
        report = Report(
            reporter=request.user,
            reported_user=reported_user_username,
            reason=reason,
            report_description=description
        )
        report.save()

        # Redirect back to the referring page or a default page
        return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))

    # If not a POST request, return an error response
    return HttpResponse("ERROR: Reports can only be submitted via POST.")

def create_scope(request):

    if request.method == 'POST':
        wallet = User.objects.get(id=request.POST.get('wallet')) 
        month = int(request.POST.get('month'))
        year = int(request.POST.get('year'))
        income_goal = float(request.POST.get('income_goal'))
        expense_goal = float(request.POST.get('expense_goal'))

        # ตรวจสอบว่าเป้าหมายเดือน/ปีนี้มีอยู่แล้วหรือไม่
        if User.objects.filter(wallet=wallet, month=month, year=year).exists():
            # เพิ่มข้อความแจ้งเตือน (หากมีอยู่แล้ว)
            return HttpResponse("ERROR, Can't create 2 scope with same month")

        # สร้างเป้าหมายใหม่
        scope = User(
            wallet=wallet,
            month=month,
            year=year,
            income_goal=income_goal,
            expense_goal=expense_goal
        )
        
        scope.save()

        return redirect(request.META.get('HTTP_REFERER', 'main'))
    else:
        # ถ้าเป็น GET ก็แสดงแบบฟอร์ม
        return HttpResponse("ERROR, Can't create_scope")

