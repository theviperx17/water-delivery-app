from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from django.contrib import messages

from .forms import SignupForm, ProfileUpdateForm
from .models import Profile
from orders.models import Order 

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, "ยินดีต้อนรับ! สมัครสมาชิกเรียบร้อยแล้ว")
            return redirect('accounts:dashboard')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    # ดึง Profile มาเตรียมไว้
    profile, created = Profile.objects.get_or_create(user=user)
    
    context = {
        'profile': profile,
        'role': profile.role
    }

    # --- 1. ผู้ดูแลระบบ (Admin) ---
    if user.is_staff:
        context['role'] = 'staff_admin'
        today = timezone.now().date()
        context['orders_today'] = Order.objects.filter(created_at__date=today).count()
        context['orders_new'] = Order.objects.filter(status='new').count()
        context['orders_out'] = Order.objects.filter(status='out_for_delivery').count()

    # --- 2. คนขับรถ (Driver) ---
    elif profile.role == 'driver':
        context['role'] = 'driver'
        
        # ดึงงานทั้งหมดที่เป็นของคนขับคนนี้
        driver_jobs = Order.objects.filter(driver=profile).order_by('-created_at')
        context['driver_jobs'] = driver_jobs

    # --- 3. ลูกค้า (Customer) ---
    else:
        context['role'] = 'customer'
        # ดึงออเดอร์ของลูกค้า
        my_orders = Order.objects.filter(customer=profile).order_by('-created_at')[:10]
        context['my_orders'] = my_orders
        
        total_spent = my_orders.aggregate(total=Sum('total_price'))['total']
        context['total_spent'] = total_spent or 0

    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile(request):
    profile_obj, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile_obj, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'อัปเดตโปรไฟล์เรียบร้อยแล้ว!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=profile_obj, user=request.user)

    context = {'form': form, 'profile': profile_obj}
    return render(request, 'accounts/profile.html', context)

# --- 👇 เพิ่มส่วนนี้เข้ามาครับ 👇 ---
@login_required
def complete_delivery(request, order_id):
    # ค้นหาออเดอร์ตาม ID
    order = get_object_or_404(Order, id=order_id)
    
    # เช็คว่าเป็น POST request เพื่อความปลอดภัย
    if request.method == "POST":
        # เปลี่ยนสถานะเป็น completed (หรือตามที่คุณตั้งไว้ใน Model เช่น 'delivered')
        order.status = 'completed'  
        order.save()
        messages.success(request, f"ส่งงานออเดอร์ #{order.id} สำเร็จเรียบร้อย!")
        
    # เด้งกลับไปหน้า Dashboard ของ Rider (namespace ของคุณคือ accounts)
    return redirect('accounts:dashboard')