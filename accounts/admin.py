from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone']
    list_filter = ['role']
    
    # ต้องมีบรรทัดนี้! เพื่อให้ OrderAdmin ค้นหาชื่อลูกค้า/คนขับได้
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone']