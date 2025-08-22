"""
Custom permission classes for the e-commerce API
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission to allow owners and staff to access objects.
    """

    def has_object_permission(self, request, view, obj):
        # Staff can access everything
        if request.user.is_staff:
            return True
        
        # Users can only access their own objects
        return obj.user == request.user


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow staff to write, but allow read access to authenticated users.
    """

    def has_permission(self, request, view):
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Write permissions only for staff
        return request.user.is_staff


class IsAdminOrOwnerReadOnly(permissions.BasePermission):
    """
    Custom permission for admin full access, owners read-only access.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin has full access
        if request.user.is_staff:
            return True

        # Owner has read-only access
        if request.method in permissions.SAFE_METHODS:
            return obj.user == request.user

        return False


class IsVerifiedUser(permissions.BasePermission):
    """
    Custom permission to only allow verified users (with email verified).
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # For this example, we'll consider all active users as verified
        # In a real application, you might check an email_verified field
        return request.user.is_active


class CanModifyReview(permissions.BasePermission):
    """
    Custom permission for review modifications.
    Users can modify their own reviews, staff can modify any review.
    """

    def has_object_permission(self, request, view, obj):
        # Staff can modify any review
        if request.user.is_staff:
            return True
        
        # Users can only modify their own reviews
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class CanViewOrder(permissions.BasePermission):
    """
    Custom permission for viewing orders.
    Users can view their own orders, staff can view all orders.
    """

    def has_object_permission(self, request, view, obj):
        # Staff can view all orders
        if request.user.is_staff:
            return True
        
        # Users can only view their own orders
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False