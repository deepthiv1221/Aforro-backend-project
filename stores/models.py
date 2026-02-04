from django.db import models


class Store(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=300)
    
    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name


class Inventory(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='inventories')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='inventories')
    quantity = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['store', 'product']
        indexes = [
            models.Index(fields=['store', 'product']),
        ]
    
    def __str__(self):
        return f'{self.store.name} - {self.product.title} ({self.quantity})'
    
    def is_in_stock(self):
        return self.quantity > 0
