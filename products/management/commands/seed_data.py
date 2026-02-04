from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
import random
from products.models import Category, Product
from stores.models import Store, Inventory


class Command(BaseCommand):
    help = 'Seed database with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--categories',
            type=int,
            default=15,
            help='Number of categories to create (default: 15)'
        )
        parser.add_argument(
            '--products',
            type=int,
            default=1000,
            help='Number of products to create (default: 1000)'
        )
        parser.add_argument(
            '--stores',
            type=int,
            default=25,
            help='Number of stores to create (default: 25)'
        )

    def handle(self, *args, **options):
        fake = Faker()
        categories_count = options['categories']
        products_count = options['products']
        stores_count = options['stores']

        self.stdout.write('Starting data seeding...')

        # Create categories
        self.stdout.write('Creating categories...')
        categories = []
        category_names = [
            'Electronics', 'Books', 'Clothing', 'Home & Garden', 'Sports',
            'Beauty', 'Toys', 'Automotive', 'Food & Grocery', 'Health',
            'Office Supplies', 'Music', 'Movies', 'Jewelry', 'Furniture'
        ]
        
        for i in range(min(categories_count, len(category_names))):
            category, created = Category.objects.get_or_create(
                name=category_names[i]
            )
            categories.append(category)
            if created:
                self.stdout.write(f'  Created category: {category.name}')

        # Create remaining categories with random names if needed
        while len(categories) < categories_count:
            name = fake.unique.word().capitalize() + ' Products'
            category, created = Category.objects.get_or_create(name=name)
            categories.append(category)
            if created:
                self.stdout.write(f'  Created category: {category.name}')

        # Create products
        self.stdout.write('Creating products...')
        products = []
        
        for i in range(products_count):
            product = Product.objects.create(
                title=fake.unique.catch_phrase(),
                description=fake.text(max_nb_chars=200),
                price=round(random.uniform(5.0, 500.0), 2),
                category=random.choice(categories)
            )
            products.append(product)
            
            if (i + 1) % 100 == 0:
                self.stdout.write(f'  Created {i + 1} products...')

        # Create stores
        self.stdout.write('Creating stores...')
        stores = []
        store_names = [
            'Main Street Store', 'Downtown Plaza', 'Mall Location', 'Suburban Center',
            'Airport Shop', 'University Store', 'Harbor Front', 'Mountain View',
            'City Center', 'West Side Market', 'East End Outlet', 'North Pole Shop',
            'South Plaza', 'Central Station', 'Garden District', 'River Walk Store',
            'Hilltop Mall', 'Valley Center', 'Beachfront Store', 'Desert Oasis',
            'Metro Station', 'Plaza Central', 'Grand Avenue', 'Market Street',
            'Commercial Drive'
        ]
        
        for i in range(min(stores_count, len(store_names))):
            store = Store.objects.create(
                name=store_names[i],
                location=fake.address()
            )
            stores.append(store)
            self.stdout.write(f'  Created store: {store.name}')

        # Create remaining stores with random names if needed
        while len(stores) < stores_count:
            store = Store.objects.create(
                name=fake.company() + ' Store',
                location=fake.address()
            )
            stores.append(store)
            self.stdout.write(f'  Created store: {store.name}')

        # Create inventory for each store
        self.stdout.write('Creating inventory...')
        inventory_created = 0
        
        for store in stores:
            # Each store gets inventory for 300-600 random products
            products_for_store = random.sample(
                products, 
                random.randint(300, min(600, len(products)))
            )
            
            for product in products_for_store:
                inventory = Inventory.objects.create(
                    store=store,
                    product=product,
                    quantity=random.randint(0, 100)
                )
                inventory_created += 1
                
                # Show progress every 1000 inventory items
                if inventory_created % 1000 == 0:
                    self.stdout.write(f'  Created {inventory_created} inventory items...')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created:\n'
                f'  - {len(categories)} categories\n'
                f'  - {len(products)} products\n'
                f'  - {len(stores)} stores\n'
                f'  - {inventory_created} inventory items'
            )
        )