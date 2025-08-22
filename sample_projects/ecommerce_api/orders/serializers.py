"""
Order and payment serializers for the e-commerce API
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from decimal import Decimal
from .models import Cart, CartItem, Order, OrderItem, Payment


class CartItemSerializer(serializers.ModelSerializer):
    """Cart item serializer"""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    product_image = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'quantity',
            'unit_price', 'total_price', 'product_image', 'is_in_stock',
            'added_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'product_name', 'product_sku', 'unit_price', 'total_price',
            'product_image', 'is_in_stock', 'added_at', 'updated_at'
        ]
    
    def get_product_image(self, obj):
        """Get product primary image"""
        primary_image = obj.product.images.filter(is_primary=True).first()
        if primary_image:
            return {
                'url': primary_image.image_url,
                'alt_text': primary_image.alt_text
            }
        first_image = obj.product.images.first()
        if first_image:
            return {
                'url': first_image.image_url,
                'alt_text': first_image.alt_text
            }
        return None
    
    def get_is_in_stock(self, obj):
        """Check if product is in stock"""
        return obj.product.is_in_stock()
    
    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class CartSerializer(serializers.ModelSerializer):
    """Cart serializer"""
    
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'session_key', 'total_items', 'total_price',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'session_key', 'total_items', 'total_price',
            'items', 'created_at', 'updated_at'
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    """Order item serializer"""
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_sku',
            'unit_price', 'quantity', 'total_price', 'created_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at']


class OrderListSerializer(serializers.ModelSerializer):
    """Order serializer for list views"""
    
    total_items = serializers.IntegerField(read_only=True)
    customer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'customer_name', 'status',
            'payment_status', 'total_amount', 'total_items',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'total_items', 'customer_name',
            'created_at', 'updated_at'
        ]
    
    def get_customer_name(self, obj):
        """Get customer name from user or shipping address"""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
        elif obj.shipping_address:
            return f"{obj.shipping_address.get('first_name', '')} {obj.shipping_address.get('last_name', '')}".strip()
        return "Guest Customer"


class OrderDetailSerializer(serializers.ModelSerializer):
    """Order serializer for detail views"""
    
    items = OrderItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    customer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'customer_name', 'status', 'payment_status',
            'subtotal', 'tax_amount', 'shipping_cost', 'discount_amount', 'total_amount',
            'shipping_address', 'billing_address', 'customer_notes', 'admin_notes',
            'total_items', 'items', 'created_at', 'updated_at',
            'confirmed_at', 'shipped_at', 'delivered_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'user', 'customer_name', 'total_items', 'items',
            'created_at', 'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at'
        ]
    
    def get_customer_name(self, obj):
        """Get customer name from user or shipping address"""
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
        elif obj.shipping_address:
            return f"{obj.shipping_address.get('first_name', '')} {obj.shipping_address.get('last_name', '')}".strip()
        return "Guest Customer"


class OrderCreateSerializer(serializers.ModelSerializer):
    """Order creation serializer"""
    
    items = OrderItemSerializer(many=True, write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'shipping_address', 'billing_address', 'customer_notes',
            'subtotal', 'tax_amount', 'shipping_cost', 'discount_amount',
            'total_amount', 'items'
        ]
    
    def validate_items(self, value):
        """Validate order items"""
        if not value:
            raise serializers.ValidationError("Order must contain at least one item")
        return value
    
    def validate_total_amount(self, value):
        """Validate total amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Total amount must be greater than 0")
        return value
    
    def create(self, validated_data):
        """Create order with items"""
        items_data = validated_data.pop('items')
        user = self.context['request'].user if self.context.get('request') and self.context['request'].user.is_authenticated else None
        
        order = Order.objects.create(user=user, **validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order


class OrderUpdateSerializer(serializers.ModelSerializer):
    """Order update serializer (for admin use)"""
    
    class Meta:
        model = Order
        fields = [
            'status', 'payment_status', 'admin_notes',
            'confirmed_at', 'shipped_at', 'delivered_at'
        ]
    
    def validate_status(self, value):
        """Validate status transitions"""
        if self.instance:
            current_status = self.instance.status
            
            # Define valid status transitions
            valid_transitions = {
                'pending': ['confirmed', 'cancelled'],
                'confirmed': ['processing', 'cancelled'],
                'processing': ['shipped', 'cancelled'],
                'shipped': ['delivered'],
                'delivered': [],  # Terminal state
                'cancelled': [],  # Terminal state
                'refunded': [],   # Terminal state
            }
            
            if value not in valid_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Cannot change status from {current_status} to {value}"
                )
        
        return value


class PaymentSerializer(serializers.ModelSerializer):
    """Payment serializer"""
    
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'order_number', 'payment_method', 'status',
            'amount', 'transaction_id', 'notes', 'processed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'processed_at', 'created_at', 'updated_at'
        ]
    
    def validate_amount(self, value):
        """Validate payment amount"""
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be greater than 0")
        return value


class CartToOrderSerializer(serializers.Serializer):
    """Serializer to convert cart to order"""
    
    shipping_address = serializers.JSONField(
        help_text="Shipping address as JSON object"
    )
    billing_address = serializers.JSONField(
        help_text="Billing address as JSON object"
    )
    customer_notes = serializers.CharField(
        max_length=500, 
        required=False, 
        allow_blank=True,
        help_text="Optional customer notes"
    )
    payment_method = serializers.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES,
        help_text="Payment method for the order"
    )
    
    def validate_shipping_address(self, value):
        """Validate shipping address structure"""
        required_fields = [
            'first_name', 'last_name', 'address_line_1', 
            'city', 'state_province', 'postal_code', 'country'
        ]
        
        for field in required_fields:
            if not value.get(field):
                raise serializers.ValidationError(
                    f"Shipping address must include {field}"
                )
        
        return value
    
    def validate_billing_address(self, value):
        """Validate billing address structure"""
        required_fields = [
            'first_name', 'last_name', 'address_line_1', 
            'city', 'state_province', 'postal_code', 'country'
        ]
        
        for field in required_fields:
            if not value.get(field):
                raise serializers.ValidationError(
                    f"Billing address must include {field}"
                )
        
        return value