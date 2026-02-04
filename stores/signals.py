from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Inventory


@receiver(post_save, sender=Inventory)
@receiver(post_delete, sender=Inventory)
def invalidate_store_inventory_cache(sender, instance, **kwargs):
    """
    Invalidate the store inventory cache when inventory items are updated or deleted.
    """
    cache_key = f'inventory_store_{instance.store_id}'
    cache.delete(cache_key)
