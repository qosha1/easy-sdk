"""
URL configuration for reviews app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet, ReviewHelpfulViewSet, ReviewResponseViewSet, ProductRatingViewSet

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'review-helpful', ReviewHelpfulViewSet, basename='reviewhelpful')
router.register(r'review-responses', ReviewResponseViewSet, basename='reviewresponse')
router.register(r'product-ratings', ProductRatingViewSet, basename='productrating')

urlpatterns = [
    path('', include(router.urls)),
]