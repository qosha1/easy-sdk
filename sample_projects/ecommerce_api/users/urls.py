"""
URL configuration for users app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AddressViewSet, WishlistViewSet, WishlistItemViewSet
from .auth_views import register, login, logout, profile, refresh_token

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'wishlists', WishlistViewSet, basename='wishlist')
router.register(r'wishlist-items', WishlistItemViewSet, basename='wishlistitem')

urlpatterns = [
    path('', include(router.urls)),
    # Authentication endpoints
    path('auth/register/', register, name='auth-register'),
    path('auth/login/', login, name='auth-login'),
    path('auth/logout/', logout, name='auth-logout'),
    path('auth/profile/', profile, name='auth-profile'),
    path('auth/refresh-token/', refresh_token, name='auth-refresh-token'),
]