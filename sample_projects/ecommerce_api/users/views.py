"""
User management views for the e-commerce API
"""

from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import UserProfile, Address, Wishlist, WishlistItem
from .serializers import (
    UserSerializer, UserProfileSerializer, AddressSerializer,
    WishlistSerializer, WishlistItemSerializer, UserRegistrationSerializer,
    UserUpdateSerializer, PasswordChangeSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user accounts.
    
    Provides user registration, profile management, and account operations.
    """
    queryset = User.objects.filter(is_active=True).order_by('-date_joined')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        else:
            return UserSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Users can only access their own data (except staff)"""
        if self.request.user.is_staff:
            return super().get_queryset()
        
        # Regular users can only see their own profile
        if self.action in ['list']:
            return User.objects.filter(id=self.request.user.id)
        
        return super().get_queryset()
    
    def get_object(self):
        """Ensure users can only access their own profile (except staff)"""
        obj = super().get_object()
        
        if not self.request.user.is_staff and obj != self.request.user:
            self.permission_denied(
                self.request,
                message="You can only access your own profile"
            )
        
        return obj
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def profile(self, request):
        """
        Get or update current user's profile information.
        """
        user = request.user
        
        if request.method == 'GET':
            try:
                profile = user.profile
                serializer = UserProfileSerializer(profile)
                return Response(serializer.data)
            except UserProfile.DoesNotExist:
                # Create profile if it doesn't exist
                profile = UserProfile.objects.create(user=user)
                serializer = UserProfileSerializer(profile)
                return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            try:
                profile = user.profile
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=user)
            
            partial = request.method == 'PATCH'
            serializer = UserProfileSerializer(
                profile, 
                data=request.data, 
                partial=partial,
                context={'request': request}
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password"""
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password changed successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user information"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class AddressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user addresses.
    
    Users can manage their shipping and billing addresses.
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return addresses for the current user only"""
        return Address.objects.filter(user=self.request.user).order_by('-is_default', '-created_at')
    
    def perform_create(self, serializer):
        """Create address for the current user"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def shipping(self, request):
        """Get user's shipping addresses"""
        addresses = self.get_queryset().filter(type='shipping')
        serializer = self.get_serializer(addresses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def billing(self, request):
        """Get user's billing addresses"""
        addresses = self.get_queryset().filter(type='billing')
        serializer = self.get_serializer(addresses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def default_shipping(self, request):
        """Get user's default shipping address"""
        try:
            address = self.get_queryset().get(type='shipping', is_default=True)
            serializer = self.get_serializer(address)
            return Response(serializer.data)
        except Address.DoesNotExist:
            return Response(
                {'message': 'No default shipping address found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def default_billing(self, request):
        """Get user's default billing address"""
        try:
            address = self.get_queryset().get(type='billing', is_default=True)
            serializer = self.get_serializer(address)
            return Response(serializer.data)
        except Address.DoesNotExist:
            return Response(
                {'message': 'No default billing address found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['patch'])
    def set_default(self, request, pk=None):
        """Set this address as default for its type"""
        address = self.get_object()
        
        # Remove default status from other addresses of the same type
        Address.objects.filter(
            user=request.user,
            type=address.type,
            is_default=True
        ).update(is_default=False)
        
        # Set this address as default
        address.is_default = True
        address.save(update_fields=['is_default'])
        
        return Response({
            'message': f'Address set as default {address.type} address',
            'is_default': address.is_default
        })


class WishlistViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing user wishlists.
    
    Provides read-only access to wishlist data. Items are managed through WishlistItemViewSet.
    """
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return wishlist for the current user only"""
        return Wishlist.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get or create wishlist for the current user"""
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        return wishlist
    
    def list(self, request):
        """Return the user's wishlist (always just one)"""
        wishlist = self.get_object()
        serializer = self.get_serializer(wishlist)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """Return the user's wishlist"""
        wishlist = self.get_object()
        serializer = self.get_serializer(wishlist)
        return Response(serializer.data)


class WishlistItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing wishlist items.
    
    Allows users to add/remove products from their wishlist.
    """
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return wishlist items for the current user only"""
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        return WishlistItem.objects.filter(wishlist=wishlist).order_by('-added_at')
    
    def perform_create(self, serializer):
        """Add item to the current user's wishlist"""
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        serializer.save(wishlist=wishlist)
    
    def create(self, request, *args, **kwargs):
        """Add product to wishlist with duplicate checking"""
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        product_id = request.data.get('product')
        
        # Check if product is already in wishlist
        if WishlistItem.objects.filter(wishlist=wishlist, product_id=product_id).exists():
            return Response(
                {'message': 'Product is already in your wishlist'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().create(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """
        Toggle product in wishlist (add if not present, remove if present).
        """
        product_id = request.data.get('product')
        if not product_id:
            return Response(
                {'error': 'product is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        
        try:
            # Try to remove if exists
            item = WishlistItem.objects.get(wishlist=wishlist, product_id=product_id)
            item.delete()
            return Response({
                'message': 'Product removed from wishlist',
                'action': 'removed',
                'in_wishlist': False
            })
        except WishlistItem.DoesNotExist:
            # Add if doesn't exist
            from products.models import Product
            try:
                product = Product.objects.get(id=product_id, status='active')
                item = WishlistItem.objects.create(wishlist=wishlist, product=product)
                serializer = self.get_serializer(item)
                return Response({
                    'message': 'Product added to wishlist',
                    'action': 'added',
                    'in_wishlist': True,
                    'item': serializer.data
                }, status=status.HTTP_201_CREATED)
            except Product.DoesNotExist:
                return Response(
                    {'error': 'Product not found or not active'},
                    status=status.HTTP_404_NOT_FOUND
                )
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Clear all items from wishlist"""
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        count = wishlist.items.count()
        wishlist.items.all().delete()
        
        return Response({
            'message': f'Removed {count} items from wishlist',
            'items_removed': count
        })
    
    @action(detail=False, methods=['post'])
    def add_multiple(self, request):
        """Add multiple products to wishlist at once"""
        product_ids = request.data.get('products', [])
        
        if not product_ids or not isinstance(product_ids, list):
            return Response(
                {'error': 'products list is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        added_items = []
        skipped_items = []
        
        from products.models import Product
        
        with transaction.atomic():
            for product_id in product_ids:
                try:
                    # Check if already in wishlist
                    if WishlistItem.objects.filter(wishlist=wishlist, product_id=product_id).exists():
                        skipped_items.append(product_id)
                        continue
                    
                    # Check if product exists and is active
                    product = Product.objects.get(id=product_id, status='active')
                    item = WishlistItem.objects.create(wishlist=wishlist, product=product)
                    added_items.append(self.get_serializer(item).data)
                
                except Product.DoesNotExist:
                    skipped_items.append(product_id)
                    continue
        
        return Response({
            'message': f'Added {len(added_items)} items to wishlist',
            'added_items': added_items,
            'skipped_items': skipped_items,
            'total_added': len(added_items),
            'total_skipped': len(skipped_items)
        }, status=status.HTTP_201_CREATED)