from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from . import views  
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # หน้าแรก: แลนดิ้งเพจ (เปลี่ยนให้เรียกใช้ view ใหม่)
    path("", views.landing_page, name="landing"), # <--- แก้ไขบรรทัดนี้

    # บัญชีผู้ใช้ (namespace = accounts)
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),

    # แคตตาล็อก/หน้าร้าน ย้ายมาอยู่ภายใต้ /shop/ (namespace = catalog)
    path("shop/", include(("catalog.urls", "catalog"), namespace="catalog")),

    # ออเดอร์/ตะกร้า (namespace = orders)
    path("orders/", include(("orders.urls", "orders"), namespace="orders")),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)