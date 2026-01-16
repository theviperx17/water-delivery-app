from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    # บทบาทสำหรับ Profile จะมีแค่ 2 อย่าง ส่วนแอดมินเราจะใช้ is_staff ของ User ในการเช็คแทน
    ROLE_CHOICES = [
        ("customer", "ผู้ใช้งาน"),
        ("driver", "คนขับรถ"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    
    # --- Field เดิมที่ปรับปรุงแล้ว ---
    phone = models.CharField(max_length=20, blank=True, verbose_name="เบอร์โทร")
    default_address = models.TextField(blank=True, verbose_name="ที่อยู่เริ่มต้น")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer", verbose_name="บทบาท")

    # === Field ที่เพิ่มเข้ามาใหม่ ===
    image = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics', verbose_name="รูปโปรไฟล์")
    birth_date = models.DateField(null=True, blank=True, verbose_name="วันเกิด")
    address_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="ละติจูด")
    address_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="ลองจิจูด")
    # ==========================

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"