"""
Management command to create sample data for the e-commerce API
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decimal import Decimal
import random

from products.models import Category, Brand, Product, ProductImage
from users.models import UserProfile, Address, Wishlist, WishlistItem
from orders.models import Cart, CartItem, Order, OrderItem, Payment
from reviews.models import Review, ProductRating


class Command(BaseCommand):
    help = 'Create sample data for testing the e-commerce API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create',
        )
        parser.add_argument(
            '--products',
            type=int,
            default=50,
            help='Number of products to create',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))
        
        # Create sample categories
        self.create_categories()
        
        # Create sample brands
        self.create_brands()
        
        # Create sample users
        self.create_users(options['users'])
        
        # Create sample products
        self.create_products(options['products'])
        
        # Create sample orders and reviews
        self.create_orders_and_reviews()
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))

    def create_categories(self):
        from django.utils.text import slugify
        
        categories = [
            ('Electronics', 'Electronic devices and accessories'),
            ('Clothing', 'Fashion and apparel'),
            ('Home & Garden', 'Home improvement and garden supplies'),
            ('Books', 'Books and literature'),
            ('Sports', 'Sports equipment and accessories'),
            ('Toys', 'Toys and games'),
            ('Beauty', 'Beauty and personal care products'),
            ('Automotive', 'Car parts and accessories'),
        ]
        
        for name, description in categories:
            slug = slugify(name)
            category, created = Category.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name, 
                    'description': description, 
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created category: {name}')

    def create_brands(self):
        from django.utils.text import slugify
        
        brands = [
            ('TechCorp', 'Leading technology brand'),
            ('FashionPlus', 'Premium fashion brand'),
            ('HomeStyle', 'Modern home solutions'),
            ('BookWorld', 'Quality book publisher'),
            ('SportMax', 'Professional sports equipment'),
            ('PlayTime', 'Fun toys for all ages'),
            ('BeautyLux', 'Luxury beauty products'),
            ('AutoParts', 'Reliable automotive parts'),
        ]
        
        for name, description in brands:
            slug = slugify(name)
            brand, created = Brand.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'description': description, 
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created brand: {name}')

    def create_users(self, count):
        for i in range(count):
            username = f'user{i+1}'
            email = f'user{i+1}@example.com'
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'User{i+1}',
                    'last_name': 'Test',
                    'is_active': True,
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                
                # Create user profile
                UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'phone_number': f'+1555000{i+1:04d}',
                        'newsletter_subscribed': random.choice([True, False]),
                    }
                )
                
                # Create sample addresses
                Address.objects.get_or_create(
                    user=user,
                    type='shipping',
                    defaults={
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'address_line_1': f'{i+1} Sample Street',
                        'city': 'Sample City',
                        'state_province': 'SC',
                        'postal_code': f'{10000 + i:05d}',
                        'country': 'US',
                        'is_default': True,
                    }
                )
                
                self.stdout.write(f'Created user: {username}')

    def create_products(self, count):
        categories = list(Category.objects.all())
        brands = list(Brand.objects.all())
        admin_user = User.objects.filter(is_superuser=True).first()
        
        if not admin_user:
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write('Created admin user')
        
        product_names = [
            'Wireless Bluetooth Headphones',
            'Cotton T-Shirt',
            'LED Desk Lamp',
            'Programming Guide',
            'Running Shoes',
            'Educational Toy Set',
            'Face Moisturizer',
            'Car Air Filter',
            'Smartphone Case',
            'Denim Jeans',
            'Coffee Maker',
            'Mystery Novel',
            'Yoga Mat',
            'Building Blocks',
            'Shampoo',
            'Brake Pads',
            'Laptop Stand',
            'Winter Jacket',
            'Garden Hose',
            'Cookbook',
        ]
        
        for i in range(min(count, len(product_names))):
            from django.utils.text import slugify
            
            name = product_names[i]
            slug = slugify(name)
            price = Decimal(str(random.uniform(10, 500)))
            sale_price = None
            
            if random.choice([True, False]):
                sale_price = price * Decimal('0.8')  # 20% discount
            
            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'description': f'High-quality {name.lower()} for everyday use.',
                    'short_description': f'Premium {name.lower()}',
                    'category': random.choice(categories),
                    'brand': random.choice(brands),
                    'price': price,
                    'sale_price': sale_price,
                    'sku': f'SKU{i+1:03d}',
                    'stock_quantity': random.randint(0, 100),
                    'status': 'active',
                    'featured': random.choice([True, False]),
                    'created_by': admin_user,
                }
            )
            
            if created:
                # Create sample product images
                ProductImage.objects.get_or_create(
                    product=product,
                    defaults={
                        'image_url': f'https://example.com/images/product{i+1}.jpg',
                        'alt_text': f'{name} image',
                        'is_primary': True,
                        'sort_order': 1,
                    }
                )
                
                self.stdout.write(f'Created product: {name}')

    def create_orders_and_reviews(self):
        users = list(User.objects.filter(is_superuser=False))
        products = list(Product.objects.all())
        
        if not users or not products:
            return
        
        # Create some orders
        for _ in range(10):
            user = random.choice(users)
            
            order = Order.objects.create(
                user=user,
                subtotal=Decimal('0'),
                total_amount=Decimal('0'),
                shipping_address={
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'address_line_1': '123 Sample Street',
                    'city': 'Sample City',
                    'state_province': 'SC',
                    'postal_code': '12345',
                    'country': 'US',
                },
                billing_address={
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'address_line_1': '123 Sample Street',
                    'city': 'Sample City',
                    'state_province': 'SC',
                    'postal_code': '12345',
                    'country': 'US',
                },
                status=random.choice(['pending', 'confirmed', 'shipped', 'delivered']),
            )
            
            # Add random products to order
            total = Decimal('0')
            for _ in range(random.randint(1, 5)):
                product = random.choice(products)
                quantity = random.randint(1, 3)
                price = product.current_price
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_sku=product.sku,
                    unit_price=price,
                    quantity=quantity,
                )
                
                total += price * quantity
            
            order.subtotal = total
            order.total_amount = total
            order.save()
            
            # Create payment
            Payment.objects.create(
                order=order,
                payment_method='credit_card',
                amount=total,
                status=random.choice(['pending', 'completed', 'failed']),
            )
        
        # Create some reviews
        for _ in range(20):
            user = random.choice(users)
            product = random.choice(products)
            
            # Check if review already exists
            if not Review.objects.filter(user=user, product=product).exists():
                Review.objects.create(
                    user=user,
                    product=product,
                    rating=random.randint(1, 5),
                    title=f'Great {product.name}!',
                    comment=f'I really enjoyed using this {product.name.lower()}. Highly recommended!',
                    is_approved=True,
                )
        
        # Update product ratings
        for product in products:
            rating_stats, created = ProductRating.objects.get_or_create(
                product=product
            )
            rating_stats.update_stats()
        
        self.stdout.write('Created sample orders and reviews')