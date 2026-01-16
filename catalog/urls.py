from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    # URLs สำหรับลูกค้า
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # URLs สำหรับ Admin/Staff
    path('manage/', views.manage_product_list, name='manage_product_list'),
    path('manage/create/', views.product_create, name='product_create'),
    path('manage/update/<int:pk>/', views.product_update, name='product_update'),
    path('manage/delete/<int:pk>/', views.product_delete, name='product_delete'),
]