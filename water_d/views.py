from django.shortcuts import render, redirect

def landing_page(request):
    # ตรวจสอบว่าผู้ใช้ล็อกอินอยู่หรือไม่
    if request.user.is_authenticated:
        # ถ้าล็อกอินอยู่ ให้ส่งต่อไปที่หน้า Dashboard ทันที
        return redirect('accounts:dashboard')
    
    # ถ้ายังไม่ล็อกอิน (เป็น Guest) ให้แสดงหน้า Landing page ปกติ
    return render(request, 'landing.html')