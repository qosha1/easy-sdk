"""
Unit tests for documentation generators
"""

import pytest
from pathlib import Path

from django_docs_generator.generators.sphinx_generator import SphinxDocumentationGenerator
from django_docs_generator.generators.typescript_generator import TypeScriptGenerator, TypeScriptType


class TestSphinxDocumentationGenerator:
    """Test Sphinx documentation generator"""
    
    def test_generator_initialization(self, test_config):
        """Test generator initialization"""
        generator = SphinxDocumentationGenerator(test_config)
        
        assert generator.config == test_config
        assert generator.output_dir == test_config.output.sphinx_output_dir
        assert generator.jinja_env is not None
    
    def test_generate_documentation(self, temp_django_project, test_config):
        """Test complete documentation generation"""
        # Set output directory within temp project
        test_config.output.sphinx_output_dir = temp_django_project / "docs" / "api"
        
        generator = SphinxDocumentationGenerator(test_config)
        generated_files = generator.generate_documentation()
        
        assert len(generated_files) > 0
        
        # Check that index.rst was created
        index_files = [f for f in generated_files if f.name == 'index.rst']
        assert len(index_files) > 0
        
        # Check that conf.py was created
        conf_files = [f for f in generated_files if f.name == 'conf.py']
        assert len(conf_files) > 0
    
    def test_generate_custom_css(self, test_config):
        """Test custom CSS generation"""
        generator = SphinxDocumentationGenerator(test_config)
        css_content = generator._generate_custom_css()
        
        assert '.api-endpoint' in css_content
        assert '.api-method' in css_content
        assert '.required-field' in css_content
    
    def test_generate_custom_js(self, test_config):
        """Test custom JavaScript generation"""
        generator = SphinxDocumentationGenerator(test_config)
        js_content = generator._generate_custom_js()
        
        assert 'copy-button' in js_content
        assert 'addEventListener' in js_content
    
    def test_generate_app_documentation(self, temp_django_project, test_config, sample_analysis_data):
        """Test app-specific documentation generation"""
        test_config.output.sphinx_output_dir = temp_django_project / "docs" / "api"
        
        generator = SphinxDocumentationGenerator(test_config)
        app_analysis = sample_analysis_data['users']
        
        generated_files = generator.generate_app_documentation('users', app_analysis)
        
        assert len(generated_files) > 0
        
        # Check that app documentation files were created
        file_names = [f.name for f in generated_files]
        assert any('index.rst' in name for name in file_names)


class TestTypeScriptType:
    """Test TypeScript type representation"""
    
    def test_type_creation(self):
        """Test TypeScript type creation"""
        ts_type = TypeScriptType("User", "")
        ts_type.is_interface = True
        ts_type.description = "User interface"
        ts_type.properties = {
            "id": "number",
            "username": "string",
            "email": "string"
        }
        
        assert ts_type.name == "User"
        assert ts_type.is_interface is True
        assert ts_type.description == "User interface"
        assert len(ts_type.properties) == 3
    
    def test_interface_generation(self):
        """Test TypeScript interface generation"""
        ts_type = TypeScriptType("User", "")
        ts_type.is_interface = True
        ts_type.description = "User interface"
        ts_type.properties = {
            "id": "number",
            "username": "string"
        }
        
        result = ts_type.to_typescript()
        
        assert "export interface User {" in result
        assert "id: number;" in result
        assert "username: string;" in result
        assert "User interface" in result
    
    def test_enum_generation(self):
        """Test TypeScript enum generation"""
        ts_type = TypeScriptType("UserStatus", "")
        ts_type.is_enum = True
        ts_type.description = "User status enum"
        ts_type.properties = {
            "ACTIVE": "'active'",
            "INACTIVE": "'inactive'"
        }
        
        result = ts_type.to_typescript()
        
        assert "export enum UserStatus {" in result
        assert "ACTIVE = 'active'," in result
        assert "INACTIVE = 'inactive'," in result
    
    def test_type_alias_generation(self):
        """Test TypeScript type alias generation"""
        ts_type = TypeScriptType("UserId", "number | string")
        ts_type.description = "User identifier type"
        
        result = ts_type.to_typescript()
        
        assert "export type UserId = number | string;" in result
        assert "User identifier type" in result


class TestTypeScriptGenerator:
    """Test TypeScript generator"""
    
    def test_generator_initialization(self, test_config):
        """Test generator initialization"""
        generator = TypeScriptGenerator(test_config)
        
        assert generator.config == test_config
        assert generator.output_dir == test_config.output.typescript_output_dir
        assert len(generator.type_mapping) > 0
    
    def test_type_mapping(self, test_config):
        """Test Django to TypeScript type mapping"""
        generator = TypeScriptGenerator(test_config)
        
        assert generator.type_mapping['string'] == 'string'
        assert generator.type_mapping['integer'] == 'number'
        assert generator.type_mapping['boolean'] == 'boolean'
        assert generator.type_mapping['datetime'] == 'string'
    
    def test_generate_types(self, temp_django_project, test_config):
        """Test TypeScript types generation"""
        test_config.output.typescript_output_dir = temp_django_project / "types"
        
        generator = TypeScriptGenerator(test_config)
        generated_files = generator.generate_types()
        
        assert len(generated_files) > 0
        
        # Check that common.d.ts was created
        common_files = [f for f in generated_files if f.name == 'common.d.ts']
        assert len(common_files) > 0
        
        # Check that index.d.ts was created
        index_files = [f for f in generated_files if f.name == 'index.d.ts']
        assert len(index_files) > 0
    
    def test_convert_field_to_typescript(self, test_config):
        """Test field to TypeScript conversion"""
        generator = TypeScriptGenerator(test_config)
        
        # Test basic field
        field_info = {'type': 'string', 'required': True}
        ts_type = generator._convert_field_to_typescript(field_info)
        assert ts_type == 'string'
        
        # Test nullable field
        field_info = {'type': 'string', 'allow_null': True}
        ts_type = generator._convert_field_to_typescript(field_info)
        assert ts_type == 'string | null'
        
        # Test list field
        field_info = {'type': 'list_string'}
        ts_type = generator._convert_field_to_typescript(field_info)
        assert ts_type == 'string[]'
        
        # Test choice field
        field_info = {
            'type': 'choice',
            'choices': [('active', 'Active'), ('inactive', 'Inactive')]
        }
        ts_type = generator._convert_field_to_typescript(field_info)
        assert "'active'" in ts_type and "'inactive'" in ts_type
    
    def test_convert_serializer_to_interface(self, test_config, sample_serializer_data):
        """Test serializer to interface conversion"""
        generator = TypeScriptGenerator(test_config)
        
        ts_interface = generator._convert_serializer_to_interface(sample_serializer_data)
        
        assert ts_interface is not None
        assert ts_interface.name == 'UserSerializer'
        assert ts_interface.is_interface is True
        assert 'username' in ts_interface.properties
        assert 'email' in ts_interface.properties
    
    def test_generate_app_types(self, temp_django_project, test_config, sample_analysis_data):
        """Test app-specific types generation"""
        test_config.output.typescript_output_dir = temp_django_project / "types"
        
        generator = TypeScriptGenerator(test_config)
        app_analysis = sample_analysis_data['users']
        
        output_file = generator.generate_app_types('users', app_analysis)
        
        assert output_file.exists()
        assert output_file.name == 'users.d.ts'
        
        # Read and verify content
        content = output_file.read_text()
        assert 'users API Types' in content
        assert 'export' in content
    
    def test_generate_serializer_variants(self, test_config, sample_serializer_data):
        """Test serializer variant generation"""
        generator = TypeScriptGenerator(test_config)
        
        variants = generator._generate_serializer_variants(sample_serializer_data)
        
        assert len(variants) > 0
        
        # Check for Create variant
        create_variants = [v for v in variants if 'Create' in v.name]
        assert len(create_variants) > 0
        
        # Check for Update variant
        update_variants = [v for v in variants if 'Update' in v.name]
        assert len(update_variants) > 0
    
    def test_basic_typescript_mapping(self, test_config):
        """Test basic TypeScript type mapping fallback"""
        generator = TypeScriptGenerator(test_config)
        
        assert generator._basic_typescript_mapping('string') == 'string'
        assert generator._basic_typescript_mapping('integer') == 'number'
        assert generator._basic_typescript_mapping('unknown_type') == 'any'