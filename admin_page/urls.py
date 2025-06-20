from django.urls import path
from .views import admin_dashboard

from . import views

urlpatterns = [
    path('admin/', admin_dashboard, name='admin_dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('orders/', views.completed_orders, name='completed_orders'),
    path('orders/<int:order_id>/', views.completed_order_detail, name='completed_order_detail'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('user/<int:user_id>/', views.user_detail, name='user_detail'),
    path('user/<int:user_id>/orders/', views.user_orders, name='user_orders'),
    path('user/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),


]
