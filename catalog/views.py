from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from .models import Product
from .forms import ProductForm  # ต้องสร้างไฟล์ forms.py ด้วยนะครับ

# --- ฟังก์ชันเช็คว่าเป็น Staff หรือไม่ ---
def is_staff_user(user):
    return user.is_authenticated and user.is_staff

# ==========================================
# ส่วนของลูกค้า (Customer Views)
# ==========================================

def product_list(request):
    """แสดงรายการสินค้าทั้งหมดสำหรับลูกค้า (เฉพาะที่ Active)"""
    products = Product.objects.filter(is_active=True)
    return render(request, 'catalog/product_list.html', {'products': products})

def product_detail(request, pk):
    """แสดงรายละเอียดสินค้า"""
    product = get_object_or_404(Product, pk=pk, is_active=True)
    return render(request, 'catalog/product_detail.html', {'product': product})


# ==========================================
# ส่วนของผู้ดูแลระบบ (Admin/Staff Views)
# ==========================================

@user_passes_test(is_staff_user)
def manage_product_list(request):
    """หน้ารายการจัดการสินค้า (เห็นทั้งหมด รวมที่ซ่อนอยู่)"""
    products = Product.objects.all().order_by('-id')
    return render(request, 'catalog/manage_product_list.html', {'products': products})

@user_passes_test(is_staff_user)
def product_create(request):
    """เพิ่มสินค้าใหม่"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'เพิ่มสินค้าใหม่เรียบร้อยแล้ว')
            return redirect('catalog:manage_product_list')
    else:
        form = ProductForm()
    
    return render(request, 'catalog/product_form.html', {
        'form': form, 
        'title': 'เพิ่มสินค้าใหม่'
    })

@user_passes_test(is_staff_user)
def product_update(request, pk):
    """แก้ไขสินค้าเดิม"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'อัปเดตข้อมูลสินค้า "{product.name}" เรียบร้อยแล้ว')
            return redirect('catalog:manage_product_list')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'catalog/product_form.html', {
        'form': form, 
        'title': f'แก้ไขสินค้า: {product.name}'
    })

@user_passes_test(is_staff_user)
def product_delete(request, pk):
    """ลบสินค้า"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, f'ลบสินค้า "{product.name}" เรียบร้อยแล้ว')
        return redirect('catalog:manage_product_list')
    
    return render(request, 'catalog/product_delete.html', {'product': product})