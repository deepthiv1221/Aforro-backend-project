from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django.core.cache import cache
from .models import Store, Inventory
from orders.models import Order, OrderItem
from orders.serializers import OrderSerializer
from .serializers import InventorySerializer


@api_view(['GET'])
def store_orders(request, store_id):
    """
    List all orders for a specific store.
    Returns orders sorted by newest first with efficient queries.
    """ 
    store = get_object_or_404(Store, id=store_id)
    
    # Efficient query with prefetch related to avoid N+1 issues
    orders = Order.objects.filter(store=store).prefetch_related(
        Prefetch(
            'order_items', 
            queryset=OrderItem.objects.select_related('product')
        )
    )
    
    serializer = OrderSerializer(orders, many=True)
    
    # Add total items count to each order
    orders_data = serializer.data
    for order_data in orders_data:
        order_data['total_items'] = len(order_data.get('order_items', []))
    
    return Response({
        'store_id': store_id,
        'store_name': store.name,
        'orders': orders_data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def store_inventory(request, store_id):
    """
    List inventory items for a specific store with caching.
    Returns items sorted alphabetically by product title.
    """
    store = get_object_or_404(Store, id=store_id)
    
    # Try to get from cache first
    cache_key = f'inventory_store_{store_id}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return Response({
            'store_id': store_id,
            'store_name': store.name,
            'inventory': cached_data,
            'from_cache': True
        }, status=status.HTTP_200_OK)
    
    # Efficient query with select_related to avoid N+1 issues
    inventory_items = Inventory.objects.filter(store=store).select_related(
        'product', 
        'product__category'
    ).order_by('product__title')
    
    serializer = InventorySerializer(inventory_items, many=True)
    
    # Cache the result for 5 minutes
    cache.set(cache_key, serializer.data, 300)
    
    return Response({
        'store_id': store_id,
        'store_name': store.name,
        'inventory': serializer.data,
        'from_cache': False
    }, status=status.HTTP_200_OK)
