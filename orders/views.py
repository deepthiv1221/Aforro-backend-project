from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from .serializers import OrderSerializer
from stores.models import Store, Inventory
from project.tasks import send_order_confirmation_email


@api_view(['POST'])
def create_order(request):
    """
    Create a new order with inventory validation and transaction handling.
    """
    store_id = request.data.get('store_id')
    order_items_data = request.data.get('items', [])
    
    if not store_id or not order_items_data:
        return Response(
            {'error': 'store_id and items are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    store = get_object_or_404(Store, id=store_id)
    
    # Validate input data
    if not isinstance(order_items_data, list):
        return Response(
            {'error': 'items must be a list'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if all products exist and validate quantities
    product_quantities = {}
    for item in order_items_data:
        product_id = item.get('product_id')
        quantity = item.get('quantity_requested')
        
        if not product_id or not quantity:
            return Response(
                {'error': 'Each item must have product_id and quantity_requested'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(quantity, int) or quantity <= 0:
            return Response(
                {'error': f'Invalid quantity for product {product_id}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product_quantities[product_id] = quantity
    
    try:
        with transaction.atomic():
            # Check inventory availability
            insufficient_stock = []
            inventory_items = {}
            
            for product_id, quantity_requested in product_quantities.items():
                try:
                    inventory = Inventory.objects.get(store=store, product_id=product_id)
                    inventory_items[product_id] = inventory
                    
                    if inventory.quantity < quantity_requested:
                        insufficient_stock.append({
                            'product_id': product_id,
                            'available': inventory.quantity,
                            'requested': quantity_requested
                        })
                except Inventory.DoesNotExist:
                    insufficient_stock.append({
                        'product_id': product_id,
                        'available': 0,
                        'requested': quantity_requested
                    })
            
            # Create order
            order_data = {
                'store': store_id,
                'order_items': [
                    {
                        'product_id': item['product_id'],
                        'quantity_requested': item['quantity_requested']
                    }
                    for item in order_items_data
                ]
            }
            
            serializer = OrderSerializer(data=order_data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            order = serializer.save()
            
            # Handle stock deduction based on availability
            if insufficient_stock:
                # Reject order if any item has insufficient stock
                order.status = Order.REJECTED
                order.save()
                
                return Response({
                    'order': OrderSerializer(order).data,
                    'status': 'REJECTED',
                    'message': 'Order rejected due to insufficient stock',
                    'insufficient_stock': insufficient_stock
                }, status=status.HTTP_201_CREATED)
            else:
                # Deduct stock and confirm order
                for product_id, quantity_requested in product_quantities.items():
                    inventory = inventory_items[product_id]
                    inventory.quantity -= quantity_requested
                    inventory.save()
                
                order.status = Order.CONFIRMED
                order.save()
                
                # Trigger async order confirmation task
                send_order_confirmation_email.delay(
                    order_id=order.id,
                    store_name=store.name,
                    customer_email='customer@example.com'  # In real app, get from request
                )
                
                return Response({
                    'order': OrderSerializer(order).data,
                    'status': 'CONFIRMED',
                    'message': 'Order confirmed and stock deducted'
                }, status=status.HTTP_201_CREATED)
                
    except Exception as e:
        return Response(
            {'error': f'Failed to process order: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
