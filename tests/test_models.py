from django.test import TestCase
from django.db import IntegrityError
from products.models import Category, Product
from stores.models import Store, Inventory
from orders.models import Order, OrderItem


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics')

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Electronics')
        self.assertEqual(str(self.category), 'Electronics')

    def test_category_unique_name(self):
        with self.assertRaises(IntegrityError):
            Category.objects.create(name='Electronics')


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            title='Smartphone',
            description='A modern smartphone',
            price=599.99,
            category=self.category
        )

    def test_product_creation(self):
        self.assertEqual(self.product.title, 'Smartphone')
        self.assertEqual(self.product.price, 599.99)
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(str(self.product), 'Smartphone')

    def test_product_category_relationship(self):
        self.assertIn(self.product, self.category.products.all())


class StoreModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            name='Main Store',
            location='123 Main Street'
        )

    def test_store_creation(self):
        self.assertEqual(self.store.name, 'Main Store')
        self.assertEqual(self.store.location, '123 Main Street')
        self.assertEqual(str(self.store), 'Main Store')


class InventoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            title='Laptop',
            price=999.99,
            category=self.category
        )
        self.store = Store.objects.create(
            name='Tech Store',
            location='456 Tech Avenue'
        )
        self.inventory = Inventory.objects.create(
            store=self.store,
            product=self.product,
            quantity=50
        )

    def test_inventory_creation(self):
        self.assertEqual(self.inventory.store, self.store)
        self.assertEqual(self.inventory.product, self.product)
        self.assertEqual(self.inventory.quantity, 50)
        self.assertEqual(str(self.inventory), 'Tech Store - Laptop (50)')

    def test_inventory_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            Inventory.objects.create(
                store=self.store,
                product=self.product,
                quantity=25
            )

    def test_is_in_stock(self):
        self.assertTrue(self.inventory.is_in_stock())
        
        # Test with zero quantity
        self.inventory.quantity = 0
        self.inventory.save()
        self.assertFalse(self.inventory.is_in_stock())


class OrderModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            title='Tablet',
            price=299.99,
            category=self.category
        )
        self.store = Store.objects.create(
            name='Gadget Store',
            location='789 Gadget Blvd'
        )
        self.order = Order.objects.create(
            store=self.store,
            status=Order.PENDING
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity_requested=2
        )

    def test_order_creation(self):
        self.assertEqual(self.order.store, self.store)
        self.assertEqual(self.order.status, Order.PENDING)
        self.assertEqual(str(self.order), f'Order #{self.order.id} - Gadget Store (PENDING)')

    def test_order_status_choices(self):
        self.assertIn(self.order.status, dict(Order.STATUS_CHOICES))

    def test_get_total_items(self):
        self.assertEqual(self.order.get_total_items(), 1)

    def test_order_item_creation(self):
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product, self.product)
        self.assertEqual(self.order_item.quantity_requested, 2)
        self.assertEqual(str(self.order_item), 'Tablet (x2)')