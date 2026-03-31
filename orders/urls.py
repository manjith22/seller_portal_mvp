from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/new/', views.create_order, name='create_order'),
    path('orders/upload/', views.bulk_upload_orders, name='bulk_upload_orders'),
    path('orders/export/', views.export_orders_excel, name='export_orders_excel'),
]
