from django.db import models
import os
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver


class Product(models.Model):
    PRODUCT_TYPES = [
        ('Skincare', 'Skincare'),
        ('Suplemnts', 'Suplements'),
        ('Snacks', 'Snacks'),
        ('Accessories', 'Accessories'),

    ]

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES, default='Other')
    product_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0) 
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
# Delete old image file on update
@receiver(pre_save, sender=Product)
def delete_old_product_image(sender, instance, **kwargs):
    if not instance.pk:
        return  # New object, nothing to delete

    try:
        old_instance = Product.objects.get(pk=instance.pk)
    except Product.DoesNotExist:
        return

    old_image = old_instance.product_image
    new_image = instance.product_image

    if old_image and old_image != new_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)

# Delete image file on product deletion
@receiver(post_delete, sender=Product)
def delete_product_image_on_delete(sender, instance, **kwargs):
    image = instance.product_image
    if image and os.path.isfile(image.path):
        os.remove(image.path)
