from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from products.models import Category, Product
from stores.models import Store, Inventory
from orders.models import Order


class OrderAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Electronics')
        self.product1 = Product.objects.create(
            title='Smartphone',
            price=599.99,
            category=self.category
        )
        self.product2 = Product.objects.create(
            title='Laptop',
            price=999.99,
            category=self.category
        )
        self.store = Store.objects.create(
            name='Tech Store',
            location='123 Tech Street'
        )
        self.inventory1 = Inventory.objects.create(
            store=self.store,
            product=self.product1,
            quantity=10
        )
        self.inventory2 = Inventory.objects.create(
            store=self.store,
            product=self.product2,
            quantity=5
        )

    def test_create_order_success(self):
        """Test successful order creation with sufficient stock"""
        url = reverse('create_order')
        data = {
            'store_id': self.store.id,
            'items': [
                {
                    'product_id': self.product1.id,
                    'quantity_requested': 2
                },
                {
                    'product_id': self.product2.id,
                    'quantity_requested': 1
                }
            ]
        }

        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'CONFIRMED')
        self.assertEqual(len(response.data['order']['order_items']), 2)
        
        # Check that inventory was deducted
        self.inventory1.refresh_from_db()
        self.inventory2.refresh_from_db()
        self.assertEqual(self.inventory1.quantity, 8)  # 10 - 2
        self.assertEqual(self.inventory2.quantity, 4)  # 5 - 1

    def test_create_order_insufficient_stock(self):
        """Test order creation with insufficient stock"""
        url = reverse('create_order')
        data = {
            'store_id': self.store.id,
            'items': [
                {
                    'product_id': self.product1.id,
                    'quantity_requested': 15  # More than available (10)
                }
            ]
        }

        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'REJECTED')
        self.assertIn('insufficient_stock', response.data)
        
        # Check that inventory was NOT deducted
        self.inventory1.refresh_from_db()
        self.assertEqual(self.inventory1.quantity, 10)

    def test_create_order_invalid_data(self):
        """Test order creation with invalid data"""
        url = reverse('create_order')
        data = {
            'store_id': self.store.id,
            'items': 'invalid_items'  # Should be a list
        }

        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class StoreAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            title='Smartphone',
            price=599.99,
            category=self.category
        )
        self.store = Store.objects.create(
            name='Tech Store',
            location='123 Tech Street'
        )
        self.inventory = Inventory.objects.create(
            store=self.store,
            product=self.product,
            quantity=10
        )

    def test_store_orders_list(self):
        """Test listing orders for a store"""
        # Create an order
        order = Order.objects.create(
            store=self.store,
            status=Order.CONFIRMED
        )
        order.order_items.create(
            product=self.product,
            quantity_requested=2
        )

        url = reverse('store_orders', kwargs={'store_id': self.store.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['store_id'], self.store.id)
        self.assertEqual(len(response.data['orders']), 1)
        self.assertEqual(response.data['orders'][0]['total_items'], 1)

    def test_store_inventory_list(self):
        """Test listing inventory for a store"""
        url = reverse('store_inventory', kwargs={'store_id': self.store.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['store_id'], self.store.id)
        self.assertEqual(len(response.data['inventory']), 1)
        self.assertEqual(response.data['inventory'][0]['product_title'], 'Smartphone')
        self.assertEqual(response.data['inventory'][0]['quantity'], 10)


class SearchAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Electronics')
        self.product1 = Product.objects.create(
            title='iPhone 15 Pro',
            description='Latest Apple smartphone',
            price=999.99,
            category=self.category
        )
        self.product2 = Product.objects.create(
            title='Samsung Galaxy S24',
            description='Latest Samsung smartphone',
            price=899.99,
            category=self.category
        )
        self.store = Store.objects.create(
            name='Phone Store',
            location='456 Phone Avenue'
        )
        Inventory.objects.create(
            store=self.store,
            product=self.product1,
            quantity=15
        )
        Inventory.objects.create(
            store=self.store,
            product=self.product2,
            quantity=8
        )

    def test_product_search(self):
        """Test product search functionality"""
        url = reverse('search_products')
        response = self.client.get(url, {'q': 'iPhone'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'iPhone 15 Pro')

    def test_product_search_with_filters(self):
        """Test product search with category filter"""
        url = reverse('search_products')
        response = self.client.get(url, {
            'category': 'Electronics',
            'min_price': 900,
            'max_price': 1000
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'iPhone 15 Pro')

    def test_autocomplete_products(self):
        """Test product autocomplete functionality"""
        url = reverse('autocomplete_products')
        response = self.client.get(url, {'q': 'iPh'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['query'], 'iPh')
        self.assertGreater(len(response.data['suggestions']), 0)
        
        # Test minimum character requirement
        response = self.client.get(url, {'q': 'ip'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SearchEnhancementsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Electronics')
        self.store = Store.objects.create(name='Phone Store', location='Test Loc')
        
    def test_autocomplete_rate_limiting(self):
        """Test rate limiting on autocomplete endpoint"""
        url = reverse('autocomplete_products')
        # Limit is 20/min. Make 21 requests.
        for _ in range(25):
            response = self.client.get(url, {'q': 'test'})
            if response.status_code == 429:
                break
        
        # The next request should fail
        response = self.client.get(url, {'q': 'test'})
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_search_relevance(self):
        """Test search relevance (PostgreSQL specific or fallback)"""
        p1 = Product.objects.create(
            title='Apple iPhone', 
            description='A smartphone', 
            price=1000, 
            category=self.category
        )
        p2 = Product.objects.create(
            title='Generic Phone', 
            description='Better than an Apple', 
            price=500, 
            category=self.category
        )
        Inventory.objects.create(store=self.store, product=p1, quantity=1)
        Inventory.objects.create(store=self.store, product=p2, quantity=1)
        
        url = reverse('search_products')
        # Sort by relevance
        response = self.client.get(url, {'q': 'Apple', 'sort_by': 'relevance'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 2)
        # P1 (Title match) should be first
        self.assertEqual(results[0]['id'], p1.id)
        self.assertEqual(results[1]['id'], p2.id)