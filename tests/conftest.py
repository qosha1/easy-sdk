"""
Pytest configuration and fixtures for Django API Documentation Generator tests
"""

import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest

from django_docs_generator.core.config import DjangoDocsConfig


@pytest.fixture
def temp_django_project():
    """Create a temporary Django project structure for testing"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        project_path = Path(tmp_dir) / "test_project"
        project_path.mkdir()
        
        # Create manage.py
        manage_py = project_path / "manage.py"
        manage_py.write_text("""#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django."
        ) from exc
    execute_from_command_line(sys.argv)
""")
        
        # Create settings.py
        settings_dir = project_path / "test_project"
        settings_dir.mkdir()
        (settings_dir / "__init__.py").touch()
        
        settings_py = settings_dir / "settings.py"
        settings_py.write_text("""
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'rest_framework',
    'api',
    'users',
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

SECRET_KEY = 'test-secret-key'
DEBUG = True
""")
        
        # Create test apps
        _create_test_app(project_path, "api")
        _create_test_app(project_path, "users")
        
        yield project_path


def _create_test_app(project_path: Path, app_name: str):
    """Create a test Django app with serializers and views"""
    app_path = project_path / app_name
    app_path.mkdir()
    
    # Create __init__.py
    (app_path / "__init__.py").touch()
    
    # Create models.py
    models_py = app_path / "models.py"
    if app_name == "users":
        models_py.write_text("""
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
""")
    else:
        models_py.write_text("""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField('Tag', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
""")
    
    # Create serializers.py
    serializers_py = app_path / "serializers.py"
    if app_name == "users":
        serializers_py.write_text("""
from rest_framework import serializers
from .models import User, Profile

class UserSerializer(serializers.ModelSerializer):
    \"\"\"Serializer for User model\"\"\"
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_verified']
        read_only_fields = ['id', 'is_verified']

class ProfileSerializer(serializers.ModelSerializer):
    \"\"\"Serializer for user profiles\"\"\"
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = ['user', 'bio', 'avatar', 'created_at']
        read_only_fields = ['created_at']

class UserCreateSerializer(serializers.ModelSerializer):
    \"\"\"Serializer for creating users\"\"\"
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
""")
    else:
        serializers_py.write_text("""
from rest_framework import serializers
from .models import Category, Post, Tag

class TagSerializer(serializers.ModelSerializer):
    \"\"\"Serializer for tags\"\"\"
    
    class Meta:
        model = Tag
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    \"\"\"Serializer for categories\"\"\"
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class PostSerializer(serializers.ModelSerializer):
    \"\"\"Serializer for blog posts\"\"\"
    author_name = serializers.CharField(source='author.username', read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author_name', 'category', 'category_id',
            'tags', 'tag_ids', 'created_at', 'updated_at', 'is_published'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class PostCreateSerializer(serializers.ModelSerializer):
    \"\"\"Serializer for creating posts\"\"\"
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'is_published']
""")
    
    # Create views.py
    views_py = app_path / "views.py"
    if app_name == "users":
        views_py.write_text("""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, Profile
from .serializers import UserSerializer, ProfileSerializer, UserCreateSerializer

class UserViewSet(viewsets.ModelViewSet):
    \"\"\"ViewSet for managing users\"\"\"
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        \"\"\"Get user profile\"\"\"
        user = self.get_object()
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=404)
        
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        \"\"\"Get current user info\"\"\"
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class ProfileViewSet(viewsets.ModelViewSet):
    \"\"\"ViewSet for user profiles\"\"\"
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
""")
    else:
        views_py.write_text("""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Post, Tag
from .serializers import CategorySerializer, PostSerializer, TagSerializer, PostCreateSerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    \"\"\"ViewSet for categories (read-only)\"\"\"
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class PostViewSet(viewsets.ModelViewSet):
    \"\"\"ViewSet for managing blog posts\"\"\"
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_published', 'author']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=False, methods=['get'])
    def published(self, request):
        \"\"\"Get only published posts\"\"\"
        queryset = self.get_queryset().filter(is_published=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class TagViewSet(viewsets.ModelViewSet):
    \"\"\"ViewSet for managing tags\"\"\"
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
""")
    
    # Create urls.py
    urls_py = app_path / "urls.py"
    if app_name == "users":
        urls_py.write_text("""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ProfileViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
""")
    else:
        urls_py.write_text("""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, PostViewSet, TagViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'posts', PostViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
""")


@pytest.fixture
def test_config(temp_django_project):
    """Create a test configuration"""
    return DjangoDocsConfig(
        project_path=temp_django_project,
        project_name="Test Django API",
        version="1.0.0",
        description="Test Django API for documentation generation",
    )


@pytest.fixture
def sample_serializer_data():
    """Sample serializer analysis data for testing"""
    return {
        'name': 'UserSerializer',
        'file_path': '/test/serializers.py',
        'base_classes': ['ModelSerializer'],
        'fields': {
            'id': {
                'name': 'id',
                'type': 'integer',
                'required': False,
                'read_only': True,
                'help_text': 'Unique identifier'
            },
            'username': {
                'name': 'username',
                'type': 'string',
                'required': True,
                'max_length': 150,
                'help_text': 'Username for login'
            },
            'email': {
                'name': 'email',
                'type': 'email',
                'required': True,
                'help_text': 'User email address'
            },
            'is_active': {
                'name': 'is_active',
                'type': 'boolean',
                'required': False,
                'default': True,
                'help_text': 'Whether user is active'
            }
        },
        'meta_info': {
            'model': 'User',
            'fields': ['id', 'username', 'email', 'is_active']
        },
        'docstring': 'Serializer for User model'
    }


@pytest.fixture
def sample_view_data():
    """Sample view analysis data for testing"""
    return {
        'name': 'UserViewSet',
        'file_path': '/test/views.py',
        'view_type': 'model_viewset',
        'base_classes': ['ModelViewSet'],
        'serializer_class': 'UserSerializer',
        'model': 'User',
        'permission_classes': ['IsAuthenticated'],
        'endpoints': [
            {
                'path': '/users/',
                'method': 'GET',
                'view_class': 'UserViewSet',
                'function_name': 'list',
                'description': 'List all users'
            },
            {
                'path': '/users/',
                'method': 'POST', 
                'view_class': 'UserViewSet',
                'function_name': 'create',
                'description': 'Create a new user'
            }
        ]
    }


@pytest.fixture
def sample_analysis_data(sample_serializer_data, sample_view_data):
    """Complete sample analysis data"""
    return {
        'users': {
            'serializers': [sample_serializer_data],
            'views': [sample_view_data],
            'app_info': {
                'name': 'users',
                'path': '/test/users',
                'has_rest_framework': True
            }
        }
    }