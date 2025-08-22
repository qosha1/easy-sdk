"""
Review and rating serializers for the e-commerce API
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Review, ReviewHelpful, ReviewResponse, ProductRating


class ReviewSerializer(serializers.ModelSerializer):
    """Review serializer"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    is_helpful_to_user = serializers.SerializerMethodField()
    response = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'product', 'product_name', 'user', 'user_name', 'order',
            'rating', 'title', 'comment', 'is_verified_purchase',
            'is_approved', 'helpful_votes', 'is_helpful_to_user',
            'response', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_name', 'product_name', 'is_verified_purchase',
            'is_approved', 'helpful_votes', 'is_helpful_to_user', 'response',
            'created_at', 'updated_at'
        ]
    
    def get_is_helpful_to_user(self, obj):
        """Check if current user found this review helpful"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.helpful_by.filter(user=request.user).exists()
        return False
    
    def get_response(self, obj):
        """Get review response if it exists"""
        if hasattr(obj, 'response'):
            return ReviewResponseSerializer(obj.response).data
        return None
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5"""
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def validate(self, data):
        """Validate review data"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            product = data.get('product')
            user = request.user
            
            # Check if user already reviewed this product (for creation only)
            if not self.instance:
                existing_review = Review.objects.filter(product=product, user=user)
                if existing_review.exists():
                    raise serializers.ValidationError(
                        "You have already reviewed this product"
                    )
        
        return data
    
    def create(self, validated_data):
        """Create review with current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        
        return super().create(validated_data)


class ReviewListSerializer(serializers.ModelSerializer):
    """Review serializer for list views (minimal data)"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'user_name', 'rating', 'title', 'comment',
            'is_verified_purchase', 'helpful_votes', 'created_at'
        ]


class ReviewResponseSerializer(serializers.ModelSerializer):
    """Review response serializer"""
    
    responder_name = serializers.CharField(source='responder.username', read_only=True)
    
    class Meta:
        model = ReviewResponse
        fields = [
            'id', 'review', 'responder', 'responder_name', 'response_text',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'responder', 'responder_name', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        """Create review response with current user as responder"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['responder'] = request.user
        
        return super().create(validated_data)


class ReviewHelpfulSerializer(serializers.ModelSerializer):
    """Review helpful serializer"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ReviewHelpful
        fields = ['id', 'review', 'user', 'user_name', 'created_at']
        read_only_fields = ['id', 'user', 'user_name', 'created_at']
    
    def create(self, validated_data):
        """Create helpful vote with current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        
        return super().create(validated_data)
    
    def validate(self, data):
        """Validate user hasn't already marked review as helpful"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            review = data.get('review')
            user = request.user
            
            if ReviewHelpful.objects.filter(review=review, user=user).exists():
                raise serializers.ValidationError(
                    "You have already marked this review as helpful"
                )
        
        return data


class ProductRatingSerializer(serializers.ModelSerializer):
    """Product rating statistics serializer"""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    rating_distribution = serializers.JSONField(read_only=True)
    
    class Meta:
        model = ProductRating
        fields = [
            'id', 'product', 'product_name', 'average_rating', 'total_reviews',
            'rating_1_count', 'rating_2_count', 'rating_3_count', 
            'rating_4_count', 'rating_5_count', 'rating_distribution', 'updated_at'
        ]
        read_only_fields = [
            'id', 'product_name', 'average_rating', 'total_reviews',
            'rating_1_count', 'rating_2_count', 'rating_3_count',
            'rating_4_count', 'rating_5_count', 'rating_distribution', 'updated_at'
        ]


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Review creation serializer with enhanced validation"""
    
    class Meta:
        model = Review
        fields = ['product', 'order', 'rating', 'title', 'comment']
    
    def validate_order(self, value):
        """Validate order belongs to current user and contains the product"""
        if value:
            request = self.context.get('request')
            if request and request.user.is_authenticated:
                # Check if order belongs to current user
                if value.user != request.user:
                    raise serializers.ValidationError(
                        "You can only review products from your own orders"
                    )
                
                # Check if order is delivered
                if value.status != 'delivered':
                    raise serializers.ValidationError(
                        "You can only review products from delivered orders"
                    )
        
        return value
    
    def validate(self, data):
        """Enhanced validation for review creation"""
        order = data.get('order')
        product = data.get('product')
        
        # If order is provided, check if product is in that order
        if order and product:
            order_items = order.items.filter(product=product)
            if not order_items.exists():
                raise serializers.ValidationError(
                    "Product must be in the specified order"
                )
        
        return super().validate(data)


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Review update serializer (limited fields)"""
    
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
    
    def validate(self, data):
        """Validate user can only update their own reviews"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and self.instance:
            if self.instance.user != request.user:
                raise serializers.ValidationError(
                    "You can only update your own reviews"
                )
        
        return data


class ReviewModerationSerializer(serializers.ModelSerializer):
    """Review moderation serializer (for admin use)"""
    
    class Meta:
        model = Review
        fields = ['is_approved', 'admin_notes']
        
    def update(self, instance, validated_data):
        """Update review approval status"""
        # If approval status changed, update product rating stats
        old_approved = instance.is_approved
        new_approved = validated_data.get('is_approved', old_approved)
        
        instance = super().update(instance, validated_data)
        
        # Update product rating statistics if approval status changed
        if old_approved != new_approved:
            rating_stats, created = ProductRating.objects.get_or_create(
                product=instance.product
            )
            rating_stats.update_stats()
        
        return instance