# catalog/models.py
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="ชื่อสินค้า")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคา")
    is_active = models.BooleanField(default=True, verbose_name="แสดงสินค้า")

    # === เพิ่ม 2 field นี้เข้ามา ===
    description = models.TextField(blank=True, verbose_name="คำอธิบาย")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="รูปภาพสินค้า")
    # ==========================

    def __str__(self):
        return self.name