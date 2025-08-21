"""
Product serializers for the e-commerce API
"""

from rest_framework import serializers
from .models import Category, Brand, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer with hierarchical support"""
    
    children = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'parent', 'parent_name',
            'is_active', 'created_at', 'updated_at', 'children'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'parent_name', 'children']
    
    def get_children(self, obj):
        """Get child categories"""
        if obj.children.exists():
            return CategorySerializer(obj.children.filter(is_active=True), many=True).data
        return []


class BrandSerializer(serializers.ModelSerializer):
    """Brand serializer"""
    
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'slug', 'description', 'logo', 'website',
            'is_active', 'created_at', 'product_count'
        ]
        read_only_fields = ['id', 'created_at', 'product_count']
    
    def get_product_count(self, obj):
        """Get number of active products for this brand"""
        return obj.products.filter(status='active').count()


class ProductImageSerializer(serializers.ModelSerializer):
    """Product image serializer"""
    
    class Meta:
        model = ProductImage
        fields = [
            'id', 'image_url', 'alt_text', 'is_primary', 'sort_order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProductListSerializer(serializers.ModelSerializer):
    """Product serializer for list views (minimal data)"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'category_name', 'brand_name',
            'price', 'sale_price', 'current_price', 'is_on_sale', 'discount_percentage',
            'sku', 'stock_quantity', 'status', 'featured', 'primary_image', 'created_at'
        ]
    
    def get_primary_image(self, obj):
        """Get primary product image"""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return {
                'url': primary_image.image_url,
                'alt_text': primary_image.alt_text
            }
        # Fallback to first image if no primary set
        first_image = obj.images.first()
        if first_image:
            return {
                'url': first_image.image_url,
                'alt_text': first_image.alt_text
            }
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Product serializer for detail views (complete data)"""
    
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    
    # Computed fields
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    is_in_stock = serializers.SerializerMethodField()
    
    # Write-only fields for creation/updates
    category_id = serializers.IntegerField(write_only=True)
    brand_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'category', 'category_id', 'brand', 'brand_id',
            'price', 'sale_price', 'cost_price', 'current_price', 
            'is_on_sale', 'discount_percentage',
            'sku', 'stock_quantity', 'track_inventory', 'allow_backorders',
            'weight', 'dimensions_length', 'dimensions_width', 'dimensions_height',
            'meta_title', 'meta_description', 'meta_keywords',
            'status', 'featured', 'is_in_stock',
            'images', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'current_price', 'is_on_sale', 'discount_percentage',
            'is_in_stock', 'created_at', 'updated_at'
        ]
    
    def get_is_in_stock(self, obj):
        """Check if product is in stock"""
        return obj.is_in_stock()
    
    def validate_price(self, value):
        """Validate that price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
    
    def validate_sale_price(self, value):
        """Validate sale price is less than regular price"""
        if value is not None:
            regular_price = self.initial_data.get('price')
            if regular_price and value >= float(regular_price):
                raise serializers.ValidationError("Sale price must be less than regular price")
        return value
    
    def validate_sku(self, value):
        """Validate SKU uniqueness"""
        if self.instance:
            # Updating existing product
            existing = Product.objects.filter(sku=value).exclude(pk=self.instance.pk)
        else:
            # Creating new product
            existing = Product.objects.filter(sku=value)
        
        if existing.exists():
            raise serializers.ValidationError("Product with this SKU already exists")
        return value


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Product serializer for create/update operations"""
    
    # Use nested serializers for related objects in write operations
    images = ProductImageSerializer(many=True, required=False)
    
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'description', 'short_description',
            'category', 'brand', 'price', 'sale_price', 'cost_price',
            'sku', 'stock_quantity', 'track_inventory', 'allow_backorders',
            'weight', 'dimensions_length', 'dimensions_width', 'dimensions_height',
            'meta_title', 'meta_description', 'meta_keywords',
            'status', 'featured', 'images'
        ]
    
    def create(self, validated_data):
        """Create product with images"""
        images_data = validated_data.pop('images', [])
        product = Product.objects.create(**validated_data)
        
        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)
        
        return product
    
    def update(self, instance, validated_data):
        """Update product and manage images"""
        images_data = validated_data.pop('images', None)
        
        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Handle images if provided
        if images_data is not None:
            # Remove existing images and add new ones
            instance.images.all().delete()
            for image_data in images_data:
                ProductImage.objects.create(product=instance, **image_data)
        
        return instance


class ProductSearchSerializer(serializers.Serializer):
    """Serializer for product search parameters"""
    
    query = serializers.CharField(required=False, help_text="Search query")
    category = serializers.IntegerField(required=False, help_text="Category ID")
    brand = serializers.IntegerField(required=False, help_text="Brand ID")
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, help_text="Minimum price")
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, help_text="Maximum price")
    in_stock_only = serializers.BooleanField(default=False, help_text="Show only in-stock products")
    featured_only = serializers.BooleanField(default=False, help_text="Show only featured products")
    on_sale_only = serializers.BooleanField(default=False, help_text="Show only products on sale")
    status = serializers.ChoiceField(
        choices=Product.STATUS_CHOICES,
        default='active',
        help_text="Product status"
    )
    
    def validate(self, data):
        """Validate search parameters"""
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        
        if min_price and max_price and min_price >= max_price:
            raise serializers.ValidationError("min_price must be less than max_price")
        
        return data