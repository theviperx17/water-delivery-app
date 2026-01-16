from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('history/', views.order_history, name='order_history'),

    # admin/staff
    path('manage/', views.manage_orders, name='manage_orders'),
    path('rounds/manage/', views.manage_rounds, name='manage_rounds'),

    # driver
    path('driver/jobs/', views.driver_jobs, name='driver_jobs'),
    path('driver/jobs/<int:order_id>/status/', views.driver_update_status, name='driver_update_status'),
    path('driver/loc/', views.driver_update_location, name='driver_update_location'),
]
