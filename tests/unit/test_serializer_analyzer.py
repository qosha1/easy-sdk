"""
Unit tests for serializer analyzer
"""

import pytest
from pathlib import Path

from django_docs_generator.analyzers.serializer_analyzer import (
    SerializerAnalyzer, SerializerField, SerializerInfo
)


class TestSerializerField:
    """Test SerializerField functionality"""
    
    def test_field_creation(self):
        """Test field creation with defaults"""
        field = SerializerField("username", "string")
        
        assert field.name == "username"
        assert field.field_type == "string"
        assert field.required is True
        assert field.read_only is False
        assert field.allow_null is False
    
    def test_field_to_dict(self):
        """Test field serialization to dict"""
        field = SerializerField("email", "email")
        field.required = True
        field.max_length = 254
        field.help_text = "User email address"
        
        field_dict = field.to_dict()
        
        assert field_dict['name'] == "email"
        assert field_dict['type'] == "email"
        assert field_dict['required'] is True
        assert field_dict['max_length'] == 254
        assert field_dict['help_text'] == "User email address"


class TestSerializerInfo:
    """Test SerializerInfo functionality"""
    
    def test_serializer_info_creation(self):
        """Test serializer info creation"""
        info = SerializerInfo("UserSerializer", "/path/to/serializers.py")
        
        assert info.name == "UserSerializer"
        assert info.file_path == "/path/to/serializers.py"
        assert len(info.fields) == 0
        assert len(info.nested_serializers) == 0
    
    def test_serializer_info_to_dict(self):
        """Test serializer info serialization"""
        info = SerializerInfo("UserSerializer", "/test/serializers.py")
        info.docstring = "Test serializer"
        
        # Add a field
        field = SerializerField("username", "string")
        info.fields["username"] = field
        
        result_dict = info.to_dict()
        
        assert result_dict['name'] == "UserSerializer"
        assert result_dict['docstring'] == "Test serializer"
        assert 'username' in result_dict['fields']
        assert result_dict['fields']['username']['type'] == "string"


class TestSerializerAnalyzer:
    """Test SerializerAnalyzer functionality"""
    
    def test_analyzer_initialization(self, test_config):
        """Test analyzer initialization"""
        analyzer = SerializerAnalyzer(test_config)
        
        assert analyzer.config == test_config
        assert len(analyzer.drf_field_types) > 0
        assert 'CharField' in analyzer.drf_field_types
        assert 'IntegerField' in analyzer.drf_field_types
    
    def test_analyze_serializer_file(self, temp_django_project, test_config):
        """Test analyzing a serializer file"""
        analyzer = SerializerAnalyzer(test_config)
        serializer_file = temp_django_project / 'users' / 'serializers.py'
        
        serializers = analyzer.analyze_serializer_file(serializer_file)
        
        assert len(serializers) > 0
        
        # Check that we found UserSerializer
        user_serializer = None
        for serializer in serializers:
            if serializer.name == 'UserSerializer':
                user_serializer = serializer
                break
        
        assert user_serializer is not None
        assert user_serializer.docstring == "Serializer for User model"
        assert len(user_serializer.base_classes) > 0
    
    def test_field_type_mapping(self, test_config):
        """Test DRF field type mapping"""
        analyzer = SerializerAnalyzer(test_config)
        
        # Test basic mappings
        assert analyzer.drf_field_types['CharField'] == 'string'
        assert analyzer.drf_field_types['IntegerField'] == 'integer'
        assert analyzer.drf_field_types['BooleanField'] == 'boolean'
        assert analyzer.drf_field_types['DateTimeField'] == 'datetime'
    
    def test_is_serializer_class(self, test_config):
        """Test serializer class identification"""
        import ast
        
        analyzer = SerializerAnalyzer(test_config)
        
        # Create AST node for serializer class
        code = """
class UserSerializer(serializers.ModelSerializer):
    pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        assert analyzer._is_serializer_class(class_node) is True
        
        # Create AST node for non-serializer class
        code = """
class User(models.Model):
    pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        assert analyzer._is_serializer_class(class_node) is False
    
    def test_get_serializer_inheritance_tree(self, test_config):
        """Test inheritance tree building"""
        analyzer = SerializerAnalyzer(test_config)
        
        # Create mock serializers
        base_serializer = SerializerInfo("BaseSerializer", "/test.py")
        base_serializer.base_classes = ["Serializer"]
        
        child_serializer = SerializerInfo("ChildSerializer", "/test.py")
        child_serializer.base_classes = ["BaseSerializer"]
        
        serializers = [base_serializer, child_serializer]
        inheritance_tree = analyzer.get_serializer_inheritance_tree(serializers)
        
        assert "BaseSerializer" in inheritance_tree
        assert "ChildSerializer" in inheritance_tree["BaseSerializer"]
    
    def test_get_field_dependencies(self, test_config):
        """Test field dependency analysis"""
        analyzer = SerializerAnalyzer(test_config)
        
        # Create mock serializer with dependencies
        serializer = SerializerInfo("UserSerializer", "/test.py")
        serializer.nested_serializers.add("ProfileSerializer")
        serializer.related_models.add("User")
        
        serializers = [serializer]
        dependencies = analyzer.get_field_dependencies(serializers)
        
        assert "UserSerializer" in dependencies
        assert "ProfileSerializer" in dependencies["UserSerializer"]
        assert "User" in dependencies["UserSerializer"]
    
    def test_analyze_app_serializers(self, temp_django_project, test_config):
        """Test analyzing all serializers in an app"""
        analyzer = SerializerAnalyzer(test_config)
        
        # Mock app info
        app_info = {
            'serializers': [str(temp_django_project / 'users' / 'serializers.py')]
        }
        
        serializers = analyzer.analyze_app_serializers('users', app_info)
        
        assert len(serializers) > 0
        
        # Verify we found expected serializers
        serializer_names = [s.name for s in serializers]
        assert 'UserSerializer' in serializer_names