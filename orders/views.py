from decimal import Decimal
from datetime import date
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.models import User

from catalog.models import Product
from accounts.models import Profile
# ตรวจสอบให้แน่ใจว่าไฟล์ accounts/utils.py มีฟังก์ชัน role_required อยู่จริง
from accounts.utils import role_required 

from .models import Order, OrderItem, DeliveryRound, DriverLocation
# ตรวจสอบว่ามีไฟล์ orders/services.py และฟังก์ชันนี้อยู่
from .services import allocate_order_to_round

CART_SESSION_KEY = 'cart'

def _get_cart(session):
    return session.setdefault(CART_SESSION_KEY, {})

# ==========================================
#  SHOPPING CART VIEWS
# ==========================================

def add_to_cart(request, product_id):
    if request.method != 'POST':
        return redirect('catalog:product_list')
    
    qty = int(request.POST.get('qty', '1'))
    qty = max(1, qty)
    
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = _get_cart(request.session)
    
    # เก็บเป็น str(id) : qty
    cart[str(product_id)] = cart.get(str(product_id), 0) + qty
    request.session.modified = True
    
    messages.success(request, f'เพิ่ม {product.name} ลงตะกร้าแล้ว')
    return redirect('orders:cart')


def remove_from_cart(request, product_id):
    cart = _get_cart(request.session)
    cart.pop(str(product_id), None)
    request.session.modified = True
    messages.success(request, 'ลบสินค้าออกจากตะกร้าแล้ว')
    return redirect('orders:cart')


def cart_view(request):
    cart = _get_cart(request.session)
    items = []
    subtotal = Decimal('0.00')
    
    for pid, qty in cart.items():
        # ดึงสินค้า (ถ้าสินค้าถูกลบไปแล้ว อาจต้อง try/except)
        p = get_object_or_404(Product, pk=int(pid))
        line_total = p.price * qty
        subtotal += line_total
        items.append({'product': p, 'qty': qty, 'line_total': line_total})
        
    return render(request, 'orders/cart.html', {'cart_items': items, 'total_price': subtotal}) # แก้ชื่อตัวแปรให้ตรงกับ template

# ==========================================
#  CHECKOUT & CUSTOMER ORDERS
# ==========================================

@login_required
def checkout(request):
    cart = _get_cart(request.session)
    if not cart:
        messages.error(request, 'ตะกร้าสินค้าว่างเปล่า')
        return redirect('catalog:product_list')

    # ดึงข้อมูล Profile ของ User
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    # ดึงรอบจัดส่งที่ยังเปิดอยู่และยังไม่ผ่านไป
    rounds = (DeliveryRound.objects
              .filter(date__gte=date.today(), status__in=['open', 'locked'])
              .order_by('date', 'start_time'))

    if request.method == 'POST':
        # รับค่าจากฟอร์ม
        address = request.POST.get('address') or profile.default_address
        lat = request.POST.get('address_lat') or None
        lng = request.POST.get('address_lng') or None
        round_id = request.POST.get('round_id')
        note = request.POST.get('note', '')

        if not round_id:
            messages.error(request, 'กรุณาเลือกรอบจัดส่ง')
            return redirect('orders:checkout')
        
        # 1. สร้าง Order
        order = Order.objects.create(
            customer=profile,
            address=address,
            address_lat=lat if lat else None,
            address_lng=lng if lng else None,
            note=note
        )

        # 2. ย้ายของจากตะกร้าลง OrderItem
        subtotal = Decimal('0.00')
        for pid, qty in cart.items():
            p = get_object_or_404(Product, pk=int(pid))
            OrderItem.objects.create(order=order, product=p, qty=qty, price=p.price)
            subtotal += p.price * qty

        # 3. อัปเดตยอดรวม
        order.total_price = subtotal
        order.save(update_fields=['total_price'])
        
        # 4. จัดสรรรอบส่ง (Service Logic)
        allocate_order_to_round(order, int(round_id))

        # 5. เคลียร์ตะกร้า
        request.session[CART_SESSION_KEY] = {}
        request.session.modified = True

        messages.success(request, f'สั่งซื้อสำเร็จ! หมายเลขคำสั่งซื้อ #{order.id}')
        return redirect('orders:order_history')

    # --- กรณี GET Request (แสดงหน้า Checkout) ---
    items = []
    subtotal = Decimal('0.00')
    for pid, qty in cart.items():
        p = get_object_or_404(Product, pk=int(pid))
        line_total = p.price * qty
        subtotal += line_total
        items.append({'product': p, 'qty': qty, 'line_total': line_total})

    return render(request, 'orders/checkout.html', {
        'cart_items': items, # แก้ชื่อตัวแปรให้ตรงกับ Template
        'total_price': subtotal,
        'profile': profile,
        'rounds': rounds,
    })


@login_required
def order_history(request):
    orders = (Order.objects
              .filter(customer__user=request.user)
              .order_by('-created_at')
              .prefetch_related('items__product', 'round'))
    return render(request, 'orders/order_history.html', {'orders': orders})

# ==========================================
#  ADMIN / STAFF MANAGEMENT
# ==========================================

@role_required('staff_admin')
def manage_orders(request):
    # แสดง 200 ออเดอร์ล่าสุด
    orders = Order.objects.select_related('driver', 'customer').order_by('-created_at')[:200]
    drivers = Profile.objects.filter(role='driver')

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        driver_id = request.POST.get('driver_id') or None
        status = request.POST.get('status')

        o = get_object_or_404(Order, pk=order_id)
        
        # อัปเดตคนขับ
        if driver_id:
            o.driver = Profile.objects.get(pk=driver_id)
        else:
            o.driver = None
            
        # อัปเดตสถานะ
        if status in dict(Order.STATUS_CHOICES):
            o.status = status
            
        o.save()
        messages.success(request, f'อัปเดตออเดอร์ #{o.id} เรียบร้อยแล้ว')
        return redirect('orders:manage_orders')

    return render(request, 'orders/manage_orders.html', {'orders': orders, 'drivers': drivers})


@role_required('staff_admin')
def manage_rounds(request):
    # ดูรอบจัดส่งตั้งแต่วันนี้เป็นต้นไป
    rounds = DeliveryRound.objects.filter(date__gte=date.today()).order_by('date', 'start_time')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        rid = request.POST.get('round_id')
        r = get_object_or_404(DeliveryRound, pk=rid)

        if action == 'pull-queue':
            # ดึงออเดอร์จาก Waiting List เข้ามารอบนี้ (ถ้าว่าง)
            space = r.capacity - r.used
            if space > 0:
                qs = (Order.objects
                      .filter(round=r, status='queued')
                      .order_by('queue_pos')[:space])
                for o in qs:
                    o.status = 'new' # หรือ status อื่นที่แปลว่าพร้อมส่ง
                    o.queue_pos = None
                    o.save(update_fields=['status', 'queue_pos'])
                messages.success(request, f'ดึงออเดอร์เข้าสู่รอบ {r} เรียบร้อยแล้ว')
            else:
                messages.warning(request, 'รอบจัดส่งนี้เต็มแล้ว')

        elif action == 'status':
            new_status = request.POST.get('status')
            valid = dict(DeliveryRound._meta.get_field('status').choices)
            if new_status in valid:
                r.status = new_status
                r.save(update_fields=['status'])

        elif action == 'assign-driver':
            did = request.POST.get('driver_id') or None
            r.driver = Profile.objects.get(pk=did) if did else None
            r.save(update_fields=['driver'])

        return redirect('orders:manage_rounds')

    drivers = Profile.objects.filter(role='driver')
    return render(request, 'orders/manage_rounds.html', {'rounds': rounds, 'drivers': drivers})

# ==========================================
#  DRIVER VIEWS
# ==========================================

@role_required('driver')
def driver_jobs(request):
    # แสดงงานของคนขับคนนั้น
    jobs = Order.objects.filter(driver__user=request.user).order_by('status', '-created_at')
    return render(request, 'orders/driver_jobs.html', {'jobs': jobs})


@role_required('driver')
def driver_update_status(request, order_id):
    o = get_object_or_404(Order, pk=order_id, driver__user=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            o.status = new_status
            o.save(update_fields=['status'])
            messages.success(request, f'อัปเดตสถานะออเดอร์ #{o.id} เป็น {o.get_status_display()}')
            
    return redirect('orders:driver_jobs')


@role_required('driver')
def driver_update_location(request):
    """API สำหรับรับพิกัด GPS จากคนขับ"""
    if request.method != 'POST':
        return HttpResponseForbidden()
    
    try:
        payload = json.loads(request.body or '{}')
        lat = payload.get('lat')
        lng = payload.get('lng')
        
        dl, _ = DriverLocation.objects.get_or_create(driver=request.user.profile)
        dl.lat = lat
        dl.lng = lng
        dl.save(update_fields=['lat', 'lng'])
        
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)