from django.test import TestCase
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient
from products.models import Category, Product
from stores.models import Store, Inventory


class CacheTest(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            title='Test Product',
            price=199.99,
            category=self.category
        )
        self.store = Store.objects.create(
            name='Test Store',
            location='123 Test Street'
        )
        self.inventory = Inventory.objects.create(
            store=self.store,
            product=self.product,
            quantity=25
        )

    def test_inventory_cache(self):
        """Test that inventory endpoint uses caching"""
        url = reverse('store_inventory', kwargs={'store_id': self.store.id})
        
        # First request should not be from cache
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)
        self.assertFalse(response1.data['from_cache'])
        
        # Second request should be from cache
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)
        self.assertTrue(response2.data['from_cache'])
        
        # Data should be the same
        self.assertEqual(
            response1.data['inventory'], 
            response2.data['inventory']
        )

    def test_cache_invalidation(self):
        """Test that cache is invalidated when inventory changes"""
        url = reverse('store_inventory', kwargs={'store_id': self.store.id})
        
        # First request
        response1 = self.client.get(url)
        initial_quantity = response1.data['inventory'][0]['quantity']
        
        # Change inventory
        self.inventory.quantity = 50
        self.inventory.save()
        
        # Cache should be invalidated automatically via signals
        # cache_key = f'inventory_store_{self.store.id}'
        # cache.delete(cache_key)
        
        # Next request should show updated quantity
        response2 = self.client.get(url)
        updated_quantity = response2.data['inventory'][0]['quantity']
        
        self.assertNotEqual(initial_quantity, updated_quantity)
        self.assertEqual(updated_quantity, 50)