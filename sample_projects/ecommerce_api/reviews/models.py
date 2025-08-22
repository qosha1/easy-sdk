"""
Review and rating models for the e-commerce API
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Review(models.Model):
    """Product review model"""
    
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # 1-5 stars
    
    # Core relationships
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews',
        help_text="Order this review is associated with (for verified purchases)"
    )
    
    # Review content
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200, help_text="Review title/summary")
    comment = models.TextField(help_text="Detailed review content")
    
    # Review metadata
    is_verified_purchase = models.BooleanField(
        default=False,
        help_text="Whether this review is from a verified purchase"
    )
    is_approved = models.BooleanField(
        default=True,
        help_text="Whether this review is approved for display"
    )
    helpful_votes = models.PositiveIntegerField(
        default=0,
        help_text="Number of users who found this review helpful"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # One review per user per product
        indexes = [
            models.Index(fields=['product', 'is_approved']),
            models.Index(fields=['user']),
            models.Index(fields=['rating']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}/5)"
    
    def save(self, *args, **kwargs):
        # Set verified purchase if order is provided
        if self.order and self.order.user == self.user:
            self.is_verified_purchase = True
        super().save(*args, **kwargs)


class ReviewHelpful(models.Model):
    """Track which users found reviews helpful"""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='helpful_by'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['review', 'user']
    
    def __str__(self):
        return f"{self.user.username} found review {self.review.id} helpful"


class ReviewResponse(models.Model):
    """Store responses/replies to reviews (from store owners, etc.)"""
    review = models.OneToOneField(
        Review,
        on_delete=models.CASCADE,
        related_name='response'
    )
    responder = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who responded (typically store owner/admin)"
    )
    response_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Response to review {self.review.id} by {self.responder.username}"


class ProductRating(models.Model):
    """Aggregated product rating statistics"""
    product = models.OneToOneField(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='rating_stats'
    )
    
    # Rating statistics
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        help_text="Average rating (0.00-5.00)"
    )
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Rating distribution
    rating_1_count = models.PositiveIntegerField(default=0)
    rating_2_count = models.PositiveIntegerField(default=0)
    rating_3_count = models.PositiveIntegerField(default=0)
    rating_4_count = models.PositiveIntegerField(default=0)
    rating_5_count = models.PositiveIntegerField(default=0)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Product Rating Statistics"
        verbose_name_plural = "Product Rating Statistics"
    
    def __str__(self):
        return f"{self.product.name} - {self.average_rating}/5.00 ({self.total_reviews} reviews)"
    
    def update_stats(self):
        """Update rating statistics based on approved reviews"""
        reviews = self.product.reviews.filter(is_approved=True)
        
        if not reviews.exists():
            self.average_rating = 0.00
            self.total_reviews = 0
            self.rating_1_count = 0
            self.rating_2_count = 0
            self.rating_3_count = 0
            self.rating_4_count = 0
            self.rating_5_count = 0
        else:
            ratings = reviews.values_list('rating', flat=True)
            self.average_rating = round(sum(ratings) / len(ratings), 2)
            self.total_reviews = len(ratings)
            
            # Update rating distribution
            self.rating_1_count = ratings.filter(rating=1).count() if hasattr(ratings, 'filter') else len([r for r in ratings if r == 1])
            self.rating_2_count = ratings.filter(rating=2).count() if hasattr(ratings, 'filter') else len([r for r in ratings if r == 2])
            self.rating_3_count = ratings.filter(rating=3).count() if hasattr(ratings, 'filter') else len([r for r in ratings if r == 3])
            self.rating_4_count = ratings.filter(rating=4).count() if hasattr(ratings, 'filter') else len([r for r in ratings if r == 4])
            self.rating_5_count = ratings.filter(rating=5).count() if hasattr(ratings, 'filter') else len([r for r in ratings if r == 5])
        
        self.save()
    
    @property
    def rating_distribution(self):
        """Get rating distribution as percentages"""
        if self.total_reviews == 0:
            return {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        return {
            5: round((self.rating_5_count / self.total_reviews) * 100, 1),
            4: round((self.rating_4_count / self.total_reviews) * 100, 1),
            3: round((self.rating_3_count / self.total_reviews) * 100, 1),
            2: round((self.rating_2_count / self.total_reviews) * 100, 1),
            1: round((self.rating_1_count / self.total_reviews) * 100, 1),
        }