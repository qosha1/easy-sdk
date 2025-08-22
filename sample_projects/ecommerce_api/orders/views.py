"""
Order and cart management views for the e-commerce API
"""

from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Cart, CartItem, Order, OrderItem, Payment
from .serializers import (
    CartSerializer, CartItemSerializer, OrderListSerializer,
    OrderDetailSerializer, OrderCreateSerializer, OrderUpdateSerializer,
    PaymentSerializer, CartToOrderSerializer
)


class CartViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing shopping carts.
    
    Provides cart management functionality for authenticated and anonymous users.
    """
    serializer_class = CartSerializer
    permission_classes = [AllowAny]  # Allow anonymous cart access
    
    def get_queryset(self):
        """Get or create cart for current user or session"""
        if self.request.user.is_authenticated:
            return Cart.objects.filter(user=self.request.user)
        else:
            # For anonymous users, use session key
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.create()
                session_key = self.request.session.session_key
            return Cart.objects.filter(session_key=session_key, user=None)
    
    def get_object(self):
        """Get or create cart for current user/session"""
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
        else:
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.create()
                session_key = self.request.session.session_key
            cart, created = Cart.objects.get_or_create(
                session_key=session_key, 
                user=None
            )
        return cart
    
    def list(self, request):
        """Return current user's cart"""
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """Return current user's cart"""
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart"""
        cart = self.get_object()
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))
        
        if not product_id:
            return Response(
                {'error': 'product is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from products.models import Product
        try:
            product = Product.objects.get(id=product_id, status='active')
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found or not active'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Update quantity if item already exists
            cart_item.quantity += quantity
            cart_item.save()
        
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['patch'])
    def update_item(self, request):
        """Update cart item quantity"""
        cart = self.get_object()
        product_id = request.data.get('product')
        quantity = request.data.get('quantity')
        
        if not product_id or quantity is None:
            return Response(
                {'error': 'product and quantity are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError("Quantity cannot be negative")
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid quantity value'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            
            if quantity == 0:
                cart_item.delete()
                return Response({'message': 'Item removed from cart'})
            else:
                cart_item.quantity = quantity
                cart_item.save()
                serializer = CartItemSerializer(cart_item)
                return Response(serializer.data)
                
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Item not found in cart'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        """Remove item from cart"""
        cart = self.get_object()
        product_id = request.data.get('product')
        
        if not product_id:
            return Response(
                {'error': 'product is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            return Response({'message': 'Item removed from cart'})
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Item not found in cart'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Clear all items from cart"""
        cart = self.get_object()
        count = cart.items.count()
        cart.items.all().delete()
        
        return Response({
            'message': f'Removed {count} items from cart',
            'items_removed': count
        })
    
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """Convert cart to order"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required for checkout'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        cart = self.get_object()
        
        if not cart.items.exists():
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CartToOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Calculate totals
            subtotal = sum(item.total_price for item in cart.items.all())
            
            # Create order
            order_data = {
                'user': request.user,
                'subtotal': subtotal,
                'tax_amount': Decimal('0.00'),  # Implement tax calculation as needed
                'shipping_cost': Decimal('0.00'),  # Implement shipping calculation
                'discount_amount': Decimal('0.00'),  # Implement discount calculation
                'total_amount': subtotal,
                'shipping_address': serializer.validated_data['shipping_address'],
                'billing_address': serializer.validated_data['billing_address'],
                'customer_notes': serializer.validated_data.get('customer_notes', ''),
            }
            
            order = Order.objects.create(**order_data)
            
            # Create order items from cart items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    product_sku=cart_item.product.sku,
                    unit_price=cart_item.unit_price,
                    quantity=cart_item.quantity
                )
            
            # Create payment record
            Payment.objects.create(
                order=order,
                payment_method=serializer.validated_data['payment_method'],
                amount=order.total_amount,
                status='pending'
            )
            
            # Clear cart after successful order creation
            cart.items.all().delete()
            
            order_serializer = OrderDetailSerializer(order)
            return Response(order_serializer.data, status=status.HTTP_201_CREATED)


class CartItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing individual cart items.
    """
    serializer_class = CartItemSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Get cart items for current user/session"""
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
        else:
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.create()
                session_key = self.request.session.session_key
            cart, created = Cart.objects.get_or_create(
                session_key=session_key, 
                user=None
            )
        
        return CartItem.objects.filter(cart=cart)


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orders.
    
    Provides order creation, viewing, and management functionality.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return orders for current user (or all if staff)"""
        if self.request.user.is_staff:
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OrderUpdateSerializer
        else:
            return OrderDetailSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['update', 'partial_update'] and not self.request.user.is_staff:
            # Only staff can update orders
            return [permissions.IsAdminUser()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """Create order with current user"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update order status (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        order = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update timestamps based on status
        if new_status == 'confirmed' and not order.confirmed_at:
            order.confirmed_at = timezone.now()
        elif new_status == 'shipped' and not order.shipped_at:
            order.shipped_at = timezone.now()
        elif new_status == 'delivered' and not order.delivered_at:
            order.delivered_at = timezone.now()
        
        order.status = new_status
        order.save()
        
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel order (user or admin)"""
        order = self.get_object()
        
        # Users can only cancel their own orders
        if not request.user.is_staff and order.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if order can be cancelled
        if order.status in ['delivered', 'cancelled', 'refunded']:
            return Response(
                {'error': f'Cannot cancel order with status: {order.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'cancelled'
        order.save()
        
        # Update payment status if needed
        try:
            payment = order.payment
            if payment.status == 'pending':
                payment.status = 'cancelled'
                payment.save()
        except Payment.DoesNotExist:
            pass
        
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """Get current user's orders"""
        orders = self.get_queryset().filter(user=request.user)
        
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = OrderListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent orders (last 30 days)"""
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=30)
        
        orders = self.get_queryset().filter(created_at__gte=cutoff_date)
        
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = OrderListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payments.
    
    Provides payment processing and management functionality.
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return payments for current user's orders (or all if staff)"""
        if self.request.user.is_staff:
            return Payment.objects.all().order_by('-created_at')
        
        # Filter payments by user's orders
        user_orders = Order.objects.filter(user=self.request.user)
        return Payment.objects.filter(order__in=user_orders).order_by('-created_at')
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only staff can modify payments directly
            return [permissions.IsAdminUser()]
        return super().get_permissions()
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update payment status (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        payment = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = new_status
        if new_status in ['completed', 'failed', 'refunded']:
            payment.processed_at = timezone.now()
        
        payment.save()
        
        # Update order payment status
        if new_status == 'completed':
            payment.order.payment_status = 'paid'
        elif new_status == 'failed':
            payment.order.payment_status = 'failed'
        elif new_status == 'refunded':
            payment.order.payment_status = 'refunded'
        
        payment.order.save(update_fields=['payment_status'])
        
        serializer = self.get_serializer(payment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process payment (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        payment = self.get_object()
        
        if payment.status != 'pending':
            return Response(
                {'error': f'Cannot process payment with status: {payment.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Simulate payment processing
        # In real implementation, integrate with payment gateway
        payment.status = 'completed'
        payment.processed_at = timezone.now()
        payment.transaction_id = f"TXN_{payment.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}"
        payment.save()
        
        # Update order status
        payment.order.payment_status = 'paid'
        if payment.order.status == 'pending':
            payment.order.status = 'confirmed'
            payment.order.confirmed_at = timezone.now()
        payment.order.save()
        
        serializer = self.get_serializer(payment)
        return Response(serializer.data)