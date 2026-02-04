from django.db import models


class Order(models.Model):
    PENDING = 'PENDING'
    CONFIRMED = 'CONFIRMED'
    REJECTED = 'REJECTED'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (REJECTED, 'Rejected'),
    ]
    
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['store', 'created_at']),
            models.Index(fields=['status']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Order #{self.id} - {self.store.name} ({self.status})'
    
    def get_total_items(self):
        return self.order_items.count()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity_requested = models.PositiveIntegerField()
    
    class Meta:
        indexes = [
            models.Index(fields=['order', 'product']),
        ]
    
    def __str__(self):
        return f'{self.product.title} (x{self.quantity_requested})'
