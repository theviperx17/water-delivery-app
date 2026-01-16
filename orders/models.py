from django.db import models
from django.contrib.auth.models import User
from catalog.models import Product
from accounts.models import Profile  # ต้อง import Profile มาใช้

class DeliveryRound(models.Model):
    TIME_CHOICES = [
        ('morning', '09:00 - 12:00 (เช้า)'),
        ('afternoon', '13:00 - 16:00 (บ่าย)'),
        ('evening', '17:00 - 20:00 (เย็น/ค่ำ)'),
    ]

    STATUS_CHOICES = [
        ('open', 'เปิดรับ'),
        ('locked', 'ปิดรับ/จัดของ'),
        ('closed', 'ปิดรอบ'),
        ('completed', 'เสร็จสิ้น'),
    ]

    date = models.DateField(verbose_name="วันที่จัดส่ง")
    time_slot = models.CharField(max_length=20, choices=TIME_CHOICES, default='morning', verbose_name="ช่วงเวลา")
    
    # ฟิลด์เวลาแบบละเอียด (เผื่อใช้คำนวณ แต่หลักๆ ใช้ time_slot)
    start_time = models.TimeField(null=True, blank=True) 
    end_time = models.TimeField(null=True, blank=True)
    
    capacity = models.PositiveIntegerField(default=30, verbose_name="รับได้สูงสุด (ออเดอร์)")
    
    # เปลี่ยนจาก User เป็น Profile เพื่อให้ filter role='driver' ได้ง่าย
    driver = models.ForeignKey(
        Profile, null=True, blank=True, on_delete=models.SET_NULL, 
        related_name='rounds', verbose_name="คนขับ"
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    # เก็บพิกัดศูนย์กระจายสินค้า (ถ้ามี)
    depot_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    depot_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ['date', 'time_slot']
        verbose_name = "รอบจัดส่ง"
        verbose_name_plural = "รอบจัดส่ง"

    def __str__(self):
        return f"{self.date} ({self.get_time_slot_display()})"

    @property
    def used(self):
        return self.orders.count()

    @property
    def remaining_capacity(self):
        return max(0, self.capacity - self.used)


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'รอชำระ/ใหม่'),
        ('processing', 'กำลังเตรียมของ'),
        ('out_for_delivery', 'กำลังจัดส่ง'),
        ('delivered', 'ส่งสำเร็จ'),
        ('cancelled', 'ยกเลิก'),
    ]
    
    PAYMENT_CHOICES = [
        ('cod', 'เก็บเงินปลายทาง'),
        ('transfer', 'โอนเงิน'),
    ]

    # ลูกค้า (Link กับ Profile)
    customer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='orders')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='cod')
    
    # ข้อมูลจัดส่ง
    address = models.TextField(verbose_name="ที่อยู่จัดส่ง")
    address_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    address_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    note = models.TextField(blank=True, null=True, verbose_name="หมายเหตุ")

    # รอบจัดส่ง (Link กับ DeliveryRound)
    round = models.ForeignKey(
        DeliveryRound, on_delete=models.SET_NULL, related_name='orders', null=True, blank=True
    )
    queue_pos = models.PositiveIntegerField(null=True, blank=True, verbose_name="คิวที่")
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # คนขับ (Assign แยกจากรอบได้ หรือดึงจากรอบก็ได้ แต่เก็บไว้ที่ Order ด้วยจะยืดหยุ่นกว่า)
    driver = models.ForeignKey(
        Profile, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_jobs'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "คำสั่งซื้อ"
        verbose_name_plural = "คำสั่งซื้อ"

    def __str__(self):
        return f"Order #{self.pk} - {self.customer}"
    
    def get_item_count(self):
        return self.items.count()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # ราคา ณ ตอนสั่งซื้อ

    @property
    def line_total(self):
        return self.qty * self.price
        
    @property
    def get_line_total(self): # เผื่อเรียกใช้ใน template
        return self.line_total

    def __str__(self):
        return f"{self.product.name} x {self.qty}"


class DriverLocation(models.Model):
    driver = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='location')
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Driver: {self.driver} ({self.lat}, {self.lng})"