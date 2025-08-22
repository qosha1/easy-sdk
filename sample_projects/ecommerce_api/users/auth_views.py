"""
Authentication views for the e-commerce API
"""

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .serializers import UserRegistrationSerializer, UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user account.
    
    Creates a new user account and returns user data with authentication token.
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        user_serializer = UserSerializer(user)
        return Response({
            'message': 'User registered successfully',
            'user': user_serializer.data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Authenticate user and return token.
    
    Accepts username/email and password, returns user data and auth token.
    """
    username_or_email = request.data.get('username')
    password = request.data.get('password')
    
    if not username_or_email or not password:
        return Response({
            'error': 'Username/email and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Try to authenticate with username first, then email
    user = None
    
    # Check if it's an email
    if '@' in username_or_email:
        try:
            user_obj = User.objects.get(email=username_or_email)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass
    else:
        user = authenticate(username=username_or_email, password=password)
    
    if user and user.is_active:
        token, created = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user)
        
        return Response({
            'message': 'Login successful',
            'user': user_serializer.data,
            'token': token.key
        })
    
    return Response({
        'error': 'Invalid credentials'
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def logout(request):
    """
    Logout user by deleting their token.
    """
    try:
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response({
            'message': 'Logout successful'
        })
    except Token.DoesNotExist:
        return Response({
            'message': 'Token not found'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def profile(request):
    """
    Get current user profile.
    """
    user_serializer = UserSerializer(request.user)
    return Response(user_serializer.data)


@api_view(['POST'])
def refresh_token(request):
    """
    Refresh user authentication token.
    """
    try:
        # Delete old token
        old_token = Token.objects.get(user=request.user)
        old_token.delete()
        
        # Create new token
        new_token = Token.objects.create(user=request.user)
        
        return Response({
            'message': 'Token refreshed successfully',
            'token': new_token.key
        })
    except Token.DoesNotExist:
        return Response({
            'error': 'Token not found'
        }, status=status.HTTP_400_BAD_REQUEST)