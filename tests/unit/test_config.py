"""
Unit tests for configuration management
"""

import tempfile
from pathlib import Path

import pytest

from easy_sdk.core.config import DjangoDocsConfig, AIConfig, GenerationConfig


class TestDjangoDocsConfig:
    """Test DjangoDocsConfig functionality"""
    
    def test_default_config_creation(self):
        """Test creating config with defaults"""
        config = DjangoDocsConfig(project_path=Path("/test/project"))
        
        assert config.project_name == "Django API"
        assert config.version == "1.0.0"
        assert config.project_path == Path("/test/project")
        assert config.ai.provider == "openai"
        assert config.generation.include_examples is True
    
    def test_config_with_custom_values(self):
        """Test creating config with custom values"""
        config = DjangoDocsConfig(
            project_path=Path("/test/project"),
            project_name="My API",
            version="2.0.0",
            description="Custom API documentation"
        )
        
        assert config.project_name == "My API"
        assert config.version == "2.0.0"
        assert config.description == "Custom API documentation"
    
    def test_should_include_app(self):
        """Test app inclusion logic"""
        # No restrictions - should include all
        config = DjangoDocsConfig(project_path=Path("/test"))
        assert config.should_include_app("api") is True
        assert config.should_include_app("users") is True
        
        # Include specific apps only
        config.include_apps = ["api", "users"]
        assert config.should_include_app("api") is True
        assert config.should_include_app("users") is True
        assert config.should_include_app("admin") is False
        
        # Exclude specific apps
        config.include_apps = None
        config.exclude_apps = ["admin", "debug"]
        assert config.should_include_app("api") is True
        assert config.should_include_app("admin") is False
        assert config.should_include_app("debug") is False
    
    def test_should_include_endpoint(self):
        """Test endpoint inclusion logic"""
        config = DjangoDocsConfig(project_path=Path("/test"))
        
        # Default excludes admin and debug
        assert config.should_include_endpoint("/api/users/") is True
        assert config.should_include_endpoint("/admin/users/") is False
        assert config.should_include_endpoint("/debug/toolbar/") is False
        
        # Custom excludes
        config.exclude_endpoints = ["/internal/"]
        assert config.should_include_endpoint("/api/users/") is True
        assert config.should_include_endpoint("/internal/stats/") is False
    
    def test_create_output_directories(self, temp_django_project):
        """Test output directory creation"""
        config = DjangoDocsConfig(project_path=temp_django_project)
        config.output.base_output_dir = temp_django_project / "output"
        config.output.sphinx_output_dir = temp_django_project / "output" / "docs"
        config.output.typescript_output_dir = temp_django_project / "output" / "types"
        
        config.create_output_directories()
        
        assert config.output.base_output_dir.exists()
        assert config.output.sphinx_output_dir.exists()
        assert config.output.typescript_output_dir.exists()
    
    def test_get_app_output_path(self, temp_django_project):
        """Test app-specific output path generation"""
        config = DjangoDocsConfig(project_path=temp_django_project)
        
        sphinx_path = config.get_app_output_path("users", "sphinx")
        typescript_path = config.get_app_output_path("users", "typescript")
        
        assert sphinx_path.name == "users.rst"
        assert "apps/users" in str(sphinx_path)
        assert typescript_path.name == "users.d.ts"
    
    def test_config_serialization(self, temp_django_project):
        """Test config to_dict and from_dict functionality"""
        original_config = DjangoDocsConfig(
            project_path=temp_django_project,
            project_name="Test API",
            version="1.5.0"
        )
        
        config_dict = original_config.to_dict()
        
        assert config_dict['project_name'] == "Test API"
        assert config_dict['version'] == "1.5.0"
        assert 'ai' in config_dict
        assert 'generation' in config_dict
        assert 'output' in config_dict


class TestAIConfig:
    """Test AI configuration"""
    
    def test_default_ai_config(self):
        """Test default AI configuration"""
        ai_config = AIConfig()
        
        assert ai_config.provider == "openai"
        assert ai_config.model == "gpt-4"
        assert ai_config.max_tokens == 4000
        assert ai_config.temperature == 0.1
    
    def test_ai_config_validation(self):
        """Test AI configuration validation"""
        # Valid provider
        ai_config = AIConfig(provider="anthropic")
        assert ai_config.provider == "anthropic"
        
        # Invalid provider
        with pytest.raises(ValueError, match="Provider must be one of"):
            AIConfig(provider="invalid")
        
        # Valid temperature
        ai_config = AIConfig(temperature=0.5)
        assert ai_config.temperature == 0.5
        
        # Invalid temperature
        with pytest.raises(ValueError, match="Temperature must be between 0 and 2"):
            AIConfig(temperature=3.0)


class TestGenerationConfig:
    """Test generation configuration"""
    
    def test_default_generation_config(self):
        """Test default generation configuration"""
        gen_config = GenerationConfig()
        
        assert gen_config.include_examples is True
        assert gen_config.generate_postman_collection is True
        assert gen_config.typescript_strict_mode is True
        assert gen_config.max_depth == 10
    
    def test_sphinx_theme_options(self):
        """Test Sphinx theme options"""
        gen_config = GenerationConfig()
        
        assert isinstance(gen_config.sphinx_theme_options, dict)
        assert 'github_url' in gen_config.sphinx_theme_options
        assert gen_config.sphinx_theme_options['show_powered_by'] is False