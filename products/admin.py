from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'product_type', 'quantity', 'is_featured')
    list_filter = ('product_type', 'is_featured')
    search_fields = ('name', 'description')
