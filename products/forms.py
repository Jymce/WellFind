from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'product_type', 'product_image', 'quantity', 'is_featured']
        widgets = {
            'product_image': forms.FileInput(attrs={'accept': 'image/*'}),
        }
