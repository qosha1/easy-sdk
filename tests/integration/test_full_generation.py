"""
Integration tests for full documentation generation workflow
"""

import pytest
from pathlib import Path

from easy_sdk.core.generator import DjangoDocsGenerator


class TestFullGeneration:
    """Test complete documentation generation workflow"""
    
    def test_full_documentation_generation(self, temp_django_project, test_config):
        """Test complete end-to-end documentation generation"""
        # Configure output directories
        test_config.output.base_output_dir = temp_django_project / "output"
        test_config.output.sphinx_output_dir = temp_django_project / "output" / "docs"
        test_config.output.typescript_output_dir = temp_django_project / "output" / "types"
        
        # Disable AI for integration test
        test_config.ai.provider = 'local'
        
        generator = DjangoDocsGenerator(str(temp_django_project), config=test_config)
        
        # Validate project
        validation_errors = generator.validate_project()
        assert len(validation_errors) == 0
        
        # Generate all documentation
        result = generator.generate_all()
        
        # Check result
        assert result.success is True
        assert len(result.errors) == 0
        assert len(result.generated_files) > 0
        
        # Verify output directories were created
        assert test_config.output.sphinx_output_dir.exists()
        assert test_config.output.typescript_output_dir.exists()
        
        # Check for key generated files
        generated_file_names = [f.name for f in result.generated_files]
        assert any('index.rst' in name for name in generated_file_names)
        assert any('conf.py' in name for name in generated_file_names)
        assert any('.d.ts' in name for name in generated_file_names)
    
    def test_sphinx_only_generation(self, temp_django_project, test_config):
        """Test Sphinx-only documentation generation"""
        test_config.output.sphinx_output_dir = temp_django_project / "docs"
        test_config.ai.provider = 'local'
        
        generator = DjangoDocsGenerator(str(temp_django_project), config=test_config)
        
        result = generator.generate_sphinx_docs()
        
        assert result.success is True
        assert len(result.generated_files) > 0
        
        # All files should be Sphinx-related
        for file_path in result.generated_files:
            assert file_path.suffix in ['.rst', '.py', '.css', '.js']
    
    def test_typescript_only_generation(self, temp_django_project, test_config):
        """Test TypeScript-only generation"""
        test_config.output.typescript_output_dir = temp_django_project / "types"
        test_config.ai.provider = 'local'
        
        generator = DjangoDocsGenerator(str(temp_django_project), config=test_config)
        
        result = generator.generate_typescript_types()
        
        assert result.success is True
        assert len(result.generated_files) > 0
        
        # All files should be TypeScript declaration files
        for file_path in result.generated_files:
            assert file_path.suffix == '.d.ts'
    
    def test_dry_run_generation(self, temp_django_project, test_config):
        """Test dry run functionality"""
        test_config.dry_run = True
        test_config.ai.provider = 'local'
        
        generator = DjangoDocsGenerator(str(temp_django_project), config=test_config)
        
        # Dry run should not create files but should analyze the project
        result = generator.generate_all()
        
        # Analysis should still work
        assert result is not None
    
    def test_app_filtering(self, temp_django_project, test_config):
        """Test app inclusion/exclusion filtering"""
        # Only include 'users' app
        test_config.include_apps = ['users']
        test_config.output.base_output_dir = temp_django_project / "output"
        test_config.ai.provider = 'local'
        
        generator = DjangoDocsGenerator(str(temp_django_project), config=test_config)
        
        # Scan the project
        scan_result = generator.scanner.scan_project()
        
        assert scan_result.success is True
        
        # Should only include 'users' app based on config
        # (Note: scanner discovers all apps, but generator should filter)
        assert 'users' in scan_result.discovered_apps
        assert 'api' in scan_result.discovered_apps  # Scanner finds all
        
        # But config should filter appropriately
        assert test_config.should_include_app('users') is True
        assert test_config.should_include_app('api') is False
    
    def test_error_handling(self, test_config):
        """Test error handling for invalid projects"""
        # Create config with non-existent project path
        test_config.project_path = Path("/non/existent/path")
        
        generator = DjangoDocsGenerator(str(test_config.project_path), config=test_config)
        
        # Validation should fail
        validation_errors = generator.validate_project()
        assert len(validation_errors) > 0
        
        # Generation should handle the error gracefully
        result = generator.generate_all()
        assert result.success is False
        assert len(result.errors) > 0
    
    def test_configuration_override(self, temp_django_project):
        """Test configuration parameter overrides"""
        # Create generator with inline config
        from easy_sdk.core.config import DjangoDocsConfig
        
        config = DjangoDocsConfig(
            project_path=temp_django_project,
            project_name="Custom Test API",
            version="2.0.0",
            exclude_apps=["api"]  # Exclude api app
        )
        config.ai.provider = 'local'
        
        generator = DjangoDocsGenerator(str(temp_django_project), config=config)
        
        # Verify configuration
        assert generator.config.project_name == "Custom Test API"
        assert generator.config.version == "2.0.0"
        assert "api" in generator.config.exclude_apps
        
        # Verify app filtering works
        assert config.should_include_app("users") is True
        assert config.should_include_app("api") is False