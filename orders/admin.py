from django.contrib import admin
from .models import Order, OrderItem, DeliveryRound, DriverLocation
from accounts.models import Profile

# --- Inline Item (แบบดิบๆ) ---
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    # เอา readonly_fields ออกก่อน กัน error
    fields = ('product', 'qty', 'price') 

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # แสดงหน้ารายการแบบง่ายๆ
    list_display = ['id', 'customer', 'status', 'driver', 'round']
    
    # --- [จุดสำคัญ] ปิดฟีเจอร์หรูหราทิ้งให้หมด ---
    # autocomplete_fields = ... (ปิด)
    # list_filter = ... (ปิด)
    # search_fields = ... (ปิด)

    # ใช้ fields แบบระบุชื่อชัดเจน
    fields = ['customer', 'address', 'status', 'driver', 'round', 'total_price']

    # ฟังก์ชันกรอง Driver แบบพื้นฐานที่สุด
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "driver":
            kwargs["queryset"] = Profile.objects.filter(role='driver')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    inlines = [OrderItemInline]

# Register ส่วนอื่นๆ แบบปกติ
admin.site.register(DeliveryRound)
admin.site.register(DriverLocation)