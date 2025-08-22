"""
Review and rating management views for the e-commerce API
"""

from django.db.models import Q, F
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .models import Review, ReviewHelpful, ReviewResponse, ProductRating
from .serializers import (
    ReviewSerializer, ReviewListSerializer, ReviewCreateSerializer,
    ReviewUpdateSerializer, ReviewModerationSerializer, ReviewHelpfulSerializer,
    ReviewResponseSerializer, ProductRatingSerializer
)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product reviews.
    
    Provides comprehensive review management with different serializers
    for different actions and user roles.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Get reviews with proper filtering and optimization"""
        queryset = Review.objects.select_related(
            'user', 'product', 'order'
        ).prefetch_related('helpful_by')
        
        # Filter by product if specified
        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Filter by user if specified (for staff)
        user_id = self.request.query_params.get('user')
        if user_id and self.request.user.is_staff:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by rating if specified
        rating = self.request.query_params.get('rating')
        if rating:
            try:
                rating = int(rating)
                if 1 <= rating <= 5:
                    queryset = queryset.filter(rating=rating)
            except (ValueError, TypeError):
                pass
        
        # Show only approved reviews for non-staff users
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_approved=True)
        
        # Default ordering
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action and user role"""
        if self.action == 'list':
            return ReviewListSerializer
        elif self.action == 'create':
            return ReviewCreateSerializer
        elif self.action in ['update', 'partial_update']:
            if self.request.user.is_staff:
                return ReviewModerationSerializer
            else:
                return ReviewUpdateSerializer
        else:
            return ReviewSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        
        return [permission() for permission in permission_classes]
    
    def get_object(self):
        """Ensure users can only modify their own reviews (except staff)"""
        obj = super().get_object()
        
        if self.action in ['update', 'partial_update', 'destroy']:
            if not self.request.user.is_staff and obj.user != self.request.user:
                self.permission_denied(
                    self.request,
                    message="You can only modify your own reviews"
                )
        
        return obj
    
    def perform_create(self, serializer):
        """Create review with current user"""
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """Update review and refresh product rating stats if needed"""
        instance = serializer.save()
        
        # Update product rating stats if approval status changed (admin action)
        if 'is_approved' in serializer.validated_data:
            rating_stats, created = ProductRating.objects.get_or_create(
                product=instance.product
            )
            rating_stats.update_stats()
    
    def perform_destroy(self, instance):
        """Delete review and update product rating stats"""
        product = instance.product
        super().perform_destroy(instance)
        
        # Update product rating stats
        rating_stats, created = ProductRating.objects.get_or_create(product=product)
        rating_stats.update_stats()
    
    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        """Get current user's reviews"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        reviews = self.get_queryset().filter(user=request.user)
        
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_approval(self, request):
        """Get reviews pending approval (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reviews = self.get_queryset().filter(is_approved=False)
        
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_helpful(self, request, pk=None):
        """Mark review as helpful"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        review = self.get_object()
        
        # Check if user already marked this review as helpful
        if ReviewHelpful.objects.filter(review=review, user=request.user).exists():
            return Response(
                {'message': 'You have already marked this review as helpful'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create helpful vote
        ReviewHelpful.objects.create(review=review, user=request.user)
        
        # Update review helpful votes count
        review.helpful_votes = F('helpful_votes') + 1
        review.save(update_fields=['helpful_votes'])
        review.refresh_from_db()
        
        return Response({
            'message': 'Review marked as helpful',
            'helpful_votes': review.helpful_votes
        })
    
    @action(detail=True, methods=['delete'])
    def unmark_helpful(self, request, pk=None):
        """Remove helpful mark from review"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        review = self.get_object()
        
        try:
            helpful = ReviewHelpful.objects.get(review=review, user=request.user)
            helpful.delete()
            
            # Update review helpful votes count
            review.helpful_votes = F('helpful_votes') - 1
            review.save(update_fields=['helpful_votes'])
            review.refresh_from_db()
            
            return Response({
                'message': 'Helpful mark removed',
                'helpful_votes': review.helpful_votes
            })
        
        except ReviewHelpful.DoesNotExist:
            return Response(
                {'message': 'You have not marked this review as helpful'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """Respond to a review (admin/staff only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        review = self.get_object()
        
        # Check if review already has a response
        if hasattr(review, 'response'):
            return Response(
                {'error': 'Review already has a response'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ReviewResponseSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save(review=review, responder=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        """Approve review (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        review = self.get_object()
        review.is_approved = True
        review.save(update_fields=['is_approved'])
        
        # Update product rating stats
        rating_stats, created = ProductRating.objects.get_or_create(
            product=review.product
        )
        rating_stats.update_stats()
        
        return Response({
            'message': 'Review approved',
            'is_approved': review.is_approved
        })
    
    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):
        """Reject review (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        review = self.get_object()
        review.is_approved = False
        review.save(update_fields=['is_approved'])
        
        # Update product rating stats
        rating_stats, created = ProductRating.objects.get_or_create(
            product=review.product
        )
        rating_stats.update_stats()
        
        return Response({
            'message': 'Review rejected',
            'is_approved': review.is_approved
        })


class ReviewHelpfulViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing review helpful votes.
    
    Allows users to mark reviews as helpful or unhelpful.
    """
    serializer_class = ReviewHelpfulSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get helpful votes for current user"""
        return ReviewHelpful.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create helpful vote with current user"""
        serializer.save(user=self.request.user)


class ReviewResponseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing review responses.
    
    Allows staff to respond to customer reviews.
    """
    serializer_class = ReviewResponseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get all review responses with optimization"""
        return ReviewResponse.objects.select_related(
            'review', 'responder'
        ).order_by('-created_at')
    
    def get_permissions(self):
        """Only staff can create/modify review responses"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Create response with current user as responder"""
        serializer.save(responder=self.request.user)


class ProductRatingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing product rating statistics.
    
    Provides read-only access to aggregated product rating data.
    """
    serializer_class = ProductRatingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Get product rating stats with optimization"""
        queryset = ProductRating.objects.select_related('product')
        
        # Filter by product if specified
        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        return queryset.order_by('-average_rating', '-total_reviews')
    
    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        """Get top-rated products"""
        min_reviews = int(request.query_params.get('min_reviews', 5))
        
        ratings = self.get_queryset().filter(
            total_reviews__gte=min_reviews
        ).order_by('-average_rating')[:20]
        
        serializer = self.get_serializer(ratings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def refresh_stats(self, request, pk=None):
        """Refresh rating statistics (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        rating_stats = self.get_object()
        rating_stats.update_stats()
        
        serializer = self.get_serializer(rating_stats)
        return Response({
            'message': 'Rating statistics refreshed',
            'data': serializer.data
        })