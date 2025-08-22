"""
User profile and related serializers for the e-commerce API
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, Address, Wishlist, WishlistItem


class UserSerializer(serializers.ModelSerializer):
    """User serializer for basic user information"""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'full_name', 'date_joined', 'last_login']
    
    def get_full_name(self, obj):
        """Get user's full name"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    
    user = UserSerializer(read_only=True)
    full_name = serializers.CharField(source='full_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'full_name', 'date_of_birth', 'gender', 
            'phone_number', 'avatar', 'newsletter_subscribed', 
            'marketing_emails', 'preferred_language', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'full_name', 'created_at', 'updated_at']
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value and not value.replace('+', '').replace(' ', '').replace('-', '').isdigit():
            raise serializers.ValidationError("Phone number must contain only digits, spaces, hyphens, and plus sign")
        return value


class AddressSerializer(serializers.ModelSerializer):
    """Address serializer"""
    
    full_name = serializers.CharField(source='full_name', read_only=True)
    formatted_address = serializers.CharField(source='formatted_address', read_only=True)
    
    class Meta:
        model = Address
        fields = [
            'id', 'type', 'first_name', 'last_name', 'full_name', 
            'company', 'address_line_1', 'address_line_2', 'city', 
            'state_province', 'postal_code', 'country', 'is_default', 
            'formatted_address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'full_name', 'formatted_address', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate address data"""
        # Ensure only one default address per type per user
        if data.get('is_default', False):
            user = self.context['request'].user if self.context.get('request') else None
            if user:
                address_type = data.get('type')
                existing_default = Address.objects.filter(
                    user=user, 
                    type=address_type, 
                    is_default=True
                )
                if self.instance:
                    existing_default = existing_default.exclude(pk=self.instance.pk)
                
                if existing_default.exists():
                    # Set other addresses to non-default
                    existing_default.update(is_default=False)
        
        return data


class WishlistItemSerializer(serializers.ModelSerializer):
    """Wishlist item serializer"""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.current_price', max_digits=10, decimal_places=2, read_only=True)
    product_image = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = WishlistItem
        fields = [
            'id', 'product', 'product_name', 'product_price', 
            'product_image', 'is_in_stock', 'added_at'
        ]
        read_only_fields = ['id', 'product_name', 'product_price', 'product_image', 'is_in_stock', 'added_at']
    
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


class WishlistSerializer(serializers.ModelSerializer):
    """Wishlist serializer"""
    
    items = WishlistItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Wishlist
        fields = [
            'id', 'user', 'total_items', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'total_items', 'items', 'created_at', 'updated_at']
    
    def get_total_items(self, obj):
        """Get total number of items in wishlist"""
        return obj.items.count()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'password', 'password_confirm'
        ]
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value
    
    def validate(self, data):
        """Validate password confirmation"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        """Create user with password"""
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """User update serializer"""
    
    profile = UserProfileSerializer(required=False)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile']
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        if self.instance:
            existing = User.objects.filter(email=value).exclude(pk=self.instance.pk)
        else:
            existing = User.objects.filter(email=value)
        
        if existing.exists():
            raise serializers.ValidationError("User with this email already exists")
        return value
    
    def update(self, instance, validated_data):
        """Update user and profile"""
        profile_data = validated_data.pop('profile', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update profile if provided
        if profile_data:
            profile = getattr(instance, 'profile', None)
            if profile:
                for attr, value in profile_data.items():
                    setattr(profile, attr, value)
                profile.save()
            else:
                UserProfile.objects.create(user=instance, **profile_data)
        
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    """Password change serializer"""
    
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
    
    def validate(self, data):
        """Validate password confirmation"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("New passwords do not match")
        return data
    
    def save(self):
        """Save new password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user