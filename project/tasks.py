from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_order_confirmation_email(order_id, store_name, customer_email):
    """
    Send order confirmation email asynchronously.
    
    This task demonstrates Celery integration and can be extended
    to include actual email sending logic with proper templates.
    """
    subject = f'Order Confirmation - #{order_id}'
    message = f"""
    Thank you for your order!
    
    Order Details:
    Order ID: {order_id}
    Store: {store_name}
    
    Your order has been confirmed and is being processed.
    
    This is a sample confirmation email sent asynchronously via Celery.
    """
    
    # In a real application, you would use proper email templates
    # and handle email sending with appropriate error handling
    
    try:
        # This would send the actual email in production
        # send_mail(
        #     subject=subject,
        #     message=message,
        #     from_email=settings.DEFAULT_FROM_EMAIL,
        #     recipient_list=[customer_email],
        #     fail_silently=False,
        # )
        
        # For demonstration, we'll just log that the task ran
        print(f"Email task executed for order {order_id}")
        print(f"Subject: {subject}")
        print(f"To: {customer_email}")
        
        return {
            'status': 'success',
            'order_id': order_id,
            'email_sent_to': customer_email
        }
    except Exception as e:
        return {
            'status': 'failed',
            'order_id': order_id,
            'error': str(e)
        }


@shared_task
def generate_daily_inventory_summary():
    """
    Generate daily inventory summary report.
    
    This task would typically run via Celery Beat on a schedule
    and could generate reports, send notifications, or update analytics.
    """
    from stores.models import Store, Inventory
    
    summary = []
    
    for store in Store.objects.all():
        total_products = store.inventories.count()
        total_quantity = sum(inv.quantity for inv in store.inventories.all())
        low_stock_items = store.inventories.filter(quantity__lt=10).count()
        
        store_summary = {
            'store_id': store.id,
            'store_name': store.name,
            'total_products': total_products,
            'total_quantity': total_quantity,
            'low_stock_items': low_stock_items
        }
        summary.append(store_summary)
    
    # In a real application, this would:
    # - Save to database
    # - Send to analytics service
    # - Email to managers
    # - Generate PDF reports
    
    print("Daily inventory summary generated:")
    for item in summary:
        print(f"Store: {item['store_name']} - Products: {item['total_products']}, "
              f"Total Qty: {item['total_quantity']}, Low Stock: {item['low_stock_items']}")
    
    return {
        'status': 'completed',
        'report_date': 'today',  # Would use actual date
        'stores_processed': len(summary),
        'summary': summary
    }


@shared_task
def preprocess_products_for_search():
    """
    Preprocess products for improved search performance.
    
    This could include:
    - Creating search indexes
    - Generating search vectors
    - Updating popularity scores
    - Caching search results
    """
    from products.models import Product
    
    # Example preprocessing logic
    processed_count = 0
    
    for product in Product.objects.all():
        # In a real application, this might:
        # - Update search vectors for full-text search
        # - Calculate popularity scores
        # - Generate search-friendly titles
        # - Update cached search data
        
        # Simple example: ensure all products have descriptions
        if not product.description:
            product.description = f"Quality {product.title} available at competitive prices."
            product.save()
        
        processed_count += 1
    
    return {
        'status': 'completed',
        'processed_products': processed_count,
        'task': 'search_preprocessing'
    }