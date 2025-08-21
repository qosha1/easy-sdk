"""
Product views for the e-commerce API
"""

from decimal import Decimal
from django.db.models import Q, F, Case, When, Value, DecimalField
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Category, Brand, Product, ProductImage
from .serializers import (
    CategorySerializer, BrandSerializer,
    ProductListSerializer, ProductDetailSerializer,
    ProductCreateUpdateSerializer, ProductImageSerializer,
    ProductSearchSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product categories.
    
    Provides CRUD operations for categories with hierarchical support.
    """
    queryset = Category.objects.filter(is_active=True).order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    lookup_field = 'slug'
    
    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """Get all products in this category"""
        category = self.get_object()
        products = Product.objects.filter(
            category=category,
            status='active'
        ).select_related('brand', 'category')
        
        # Apply pagination
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def subcategories(self, request, slug=None):
        """Get all subcategories of this category"""
        category = self.get_object()
        subcategories = category.children.filter(is_active=True)
        serializer = self.get_serializer(subcategories, many=True)
        return Response(serializer.data)


class BrandViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product brands.
    
    Provides CRUD operations for brands.
    """
    queryset = Brand.objects.filter(is_active=True).order_by('name')
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    lookup_field = 'slug'
    
    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """Get all products from this brand"""
        brand = self.get_object()
        products = Product.objects.filter(
            brand=brand,
            status='active'
        ).select_related('brand', 'category').prefetch_related('images')
        
        # Apply pagination
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products.
    
    Provides comprehensive CRUD operations for products with advanced filtering,
    search capabilities, and various product-specific actions.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'short_description', 'sku']
    ordering_fields = [
        'name', 'price', 'created_at', 'stock_quantity', 'status'
    ]
    ordering = ['-created_at']
    lookup_field = 'slug'
    
    # Filtering options
    filterset_fields = {
        'category': ['exact'],
        'brand': ['exact'],
        'price': ['gte', 'lte'],
        'status': ['exact'],
        'featured': ['exact'],
        'track_inventory': ['exact'],
    }
    
    def get_queryset(self):
        """Get queryset with optimized queries"""
        queryset = Product.objects.select_related(
            'category', 'brand', 'created_by'
        ).prefetch_related('images')
        
        # Filter by status for regular users
        if not self.request.user.is_staff:
            queryset = queryset.filter(status='active')
        
        return queryset.annotate(
            # Add computed fields as annotations for better performance
            current_price=Case(
                When(sale_price__isnull=False, sale_price__lt=F('price'), then=F('sale_price')),
                default=F('price'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            ),
            is_on_sale=Case(
                When(sale_price__isnull=False, sale_price__lt=F('price'), then=Value(True)),
                default=Value(False),
                output_field=DecimalField()
            )
        )
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        else:
            return ProductDetailSerializer
    
    def perform_create(self, serializer):
        """Set created_by field when creating products"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products"""
        products = self.get_queryset().filter(featured=True, status='active')
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def on_sale(self, request):
        """Get products currently on sale"""
        products = self.get_queryset().filter(
            sale_price__isnull=False,
            sale_price__lt=F('price'),
            status='active'
        )
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """
        Advanced product search with multiple filters.
        
        Accepts search parameters in request body for complex queries.
        """
        search_serializer = ProductSearchSerializer(data=request.data)
        search_serializer.is_valid(raise_exception=True)
        
        filters = Q()
        params = search_serializer.validated_data
        
        # Text search
        if 'query' in params:
            query = params['query']
            filters &= (
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(short_description__icontains=query) |
                Q(sku__icontains=query)
            )
        
        # Category filter
        if 'category' in params:
            filters &= Q(category_id=params['category'])
        
        # Brand filter
        if 'brand' in params:
            filters &= Q(brand_id=params['brand'])
        
        # Price range
        if 'min_price' in params:
            filters &= Q(price__gte=params['min_price'])
        if 'max_price' in params:
            filters &= Q(price__lte=params['max_price'])
        
        # Stock filter
        if params.get('in_stock_only', False):
            filters &= Q(
                Q(track_inventory=False) |
                Q(stock_quantity__gt=0) |
                Q(allow_backorders=True)
            )
        
        # Featured filter
        if params.get('featured_only', False):
            filters &= Q(featured=True)
        
        # Sale filter
        if params.get('on_sale_only', False):
            filters &= Q(sale_price__isnull=False, sale_price__lt=F('price'))
        
        # Status filter
        filters &= Q(status=params.get('status', 'active'))
        
        # Apply filters
        products = self.get_queryset().filter(filters)
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_image(self, request, slug=None):
        """Add an image to a product"""
        product = self.get_object()
        serializer = ProductImageSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def remove_image(self, request, slug=None):
        """Remove an image from a product"""
        product = self.get_object()
        image_id = request.data.get('image_id')
        
        if not image_id:
            return Response(
                {'error': 'image_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            image = product.images.get(id=image_id)
            image.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProductImage.DoesNotExist:
            return Response(
                {'error': 'Image not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['patch'])
    def update_stock(self, request, slug=None):
        """Update product stock quantity"""
        product = self.get_object()
        stock_quantity = request.data.get('stock_quantity')
        
        if stock_quantity is None:
            return Response(
                {'error': 'stock_quantity is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            stock_quantity = int(stock_quantity)
            if stock_quantity < 0:
                raise ValueError("Stock quantity cannot be negative")
            
            product.stock_quantity = stock_quantity
            product.save(update_fields=['stock_quantity'])
            
            return Response({
                'message': 'Stock updated successfully',
                'stock_quantity': product.stock_quantity,
                'is_in_stock': product.is_in_stock()
            })
        
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid stock_quantity value'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['patch'])
    def toggle_featured(self, request, slug=None):
        """Toggle product featured status"""
        product = self.get_object()
        product.featured = not product.featured
        product.save(update_fields=['featured'])
        
        return Response({
            'message': f'Product {"featured" if product.featured else "unfeatured"}',
            'featured': product.featured
        })


class ProductImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product images.
    
    Provides CRUD operations for product images with ordering support.
    """
    queryset = ProductImage.objects.all().order_by('sort_order')
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['sort_order', 'created_at']
    ordering = ['sort_order']
    
    def get_queryset(self):
        """Filter images by product if specified"""
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product')
        
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        return queryset
    
    @action(detail=True, methods=['patch'])
    def set_primary(self, request, pk=None):
        """Set this image as the primary image for the product"""
        image = self.get_object()
        
        # Remove primary status from other images of the same product
        ProductImage.objects.filter(
            product=image.product,
            is_primary=True
        ).update(is_primary=False)
        
        # Set this image as primary
        image.is_primary = True
        image.save(update_fields=['is_primary'])
        
        return Response({
            'message': 'Image set as primary',
            'is_primary': image.is_primary
        })