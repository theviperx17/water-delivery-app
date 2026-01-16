# catalog/forms.py
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'is_active']
        labels = {
            'name': 'ชื่อสินค้า',
            'description': 'คำอธิบาย',
            'price': 'ราคา',
            'image': 'รูปภาพสินค้า',
            'is_active': 'แสดงสินค้า (Active)',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }