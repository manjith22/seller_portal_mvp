from django.contrib import admin
from .models import SellerProfile, Order


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'seller_code', 'user', 'is_active', 'created_at')
    search_fields = ('display_name', 'seller_code', 'user__username')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer_name', 'seller', 'product', 'amount', 'payment_type', 'status', 'order_date')
    list_filter = ('seller', 'payment_type', 'status', 'order_date')
    search_fields = ('order_id', 'customer_name', 'phone', 'product', 'tag')
