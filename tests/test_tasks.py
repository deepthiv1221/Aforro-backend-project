from django.test import TestCase
from project.tasks import send_order_confirmation_email, generate_daily_inventory_summary


class CeleryTaskTest(TestCase):
    def test_send_order_confirmation_email(self):
        """Test the order confirmation email task"""
        result = send_order_confirmation_email(
            order_id=123,
            store_name='Test Store',
            customer_email='test@example.com'
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['order_id'], 123)
        self.assertEqual(result['email_sent_to'], 'test@example.com')

    def test_generate_daily_inventory_summary(self):
        """Test the inventory summary generation task"""
        from products.models import Category, Product
        from stores.models import Store, Inventory
        
        # Create test data
        category = Category.objects.create(name='Test Category')
        product = Product.objects.create(
            title='Test Product',
            price=99.99,
            category=category
        )
        store = Store.objects.create(
            name='Test Store',
            location='123 Test Street'
        )
        Inventory.objects.create(
            store=store,
            product=product,
            quantity=15
        )
        
        result = generate_daily_inventory_summary()
        
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['stores_processed'], 1)
        self.assertEqual(len(result['summary']), 1)
        
        summary = result['summary'][0]
        self.assertEqual(summary['store_name'], 'Test Store')
        self.assertEqual(summary['total_products'], 1)
        self.assertEqual(summary['total_quantity'], 15)