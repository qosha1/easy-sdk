"""
Django API Documentation Generator Usage Examples

This file demonstrates various ways to use the Django API Documentation Generator
in your Python applications and scripts.
"""

import os
from pathlib import Path

from django_docs_generator import DjangoDocsGenerator, DjangoDocsConfig


def example_basic_usage():
    """Basic usage example with minimal configuration"""
    print("🚀 Example 1: Basic Usage")
    
    # Point to your Django project
    project_path = "/path/to/your/django/project"
    
    # Create generator with default configuration
    generator = DjangoDocsGenerator(project_path)
    
    # Generate all documentation
    result = generator.generate_all()
    
    if result.success:
        print(f"✅ Successfully generated {len(result.generated_files)} files!")
        print(f"📁 Documentation available at: {generator.config.output.base_output_dir}")
    else:
        print("❌ Generation failed:")
        for error in result.errors:
            print(f"  - {error}")


def example_custom_configuration():
    """Example with custom configuration"""
    print("🔧 Example 2: Custom Configuration")
    
    # Create custom configuration
    config = DjangoDocsConfig(
        project_path=Path("/path/to/django/project"),
        project_name="My Awesome API",
        version="2.1.0",
        description="Comprehensive API documentation for My Awesome API",
        author="John Doe <john@example.com>"
    )
    
    # Customize AI settings
    config.ai.provider = "openai"
    config.ai.model = "gpt-4"
    config.ai.temperature = 0.2
    
    # Customize output settings
    config.output.base_output_dir = Path("./custom-docs")
    config.output.typescript_output_dir = Path("./frontend/types")
    
    # App filtering
    config.include_apps = ["api", "users", "products"]
    config.exclude_apps = ["admin", "debug"]
    
    # Generation options
    config.generation.include_examples = True
    config.generation.typescript_strict_mode = True
    
    # Create generator with custom config
    generator = DjangoDocsGenerator(str(config.project_path), config=config)
    
    # Validate project first
    validation_errors = generator.validate_project()
    if validation_errors:
        print("⚠️ Project validation issues:")
        for error in validation_errors:
            print(f"  - {error}")
        return
    
    # Generate documentation
    result = generator.generate_all()
    result.print_summary(generator.console)


def example_typescript_only():
    """Generate only TypeScript definitions"""
    print("📝 Example 3: TypeScript Only")
    
    config = DjangoDocsConfig(
        project_path=Path("/path/to/django/project"),
        project_name="TypeScript API Types"
    )
    
    # Configure TypeScript-specific settings
    config.generation.typescript_strict_mode = True
    config.output.typescript_output_dir = Path("./src/types")
    
    generator = DjangoDocsGenerator(str(config.project_path), config=config)
    
    # Generate only TypeScript types
    result = generator.generate_typescript_types()
    
    if result.success:
        print("📝 TypeScript definitions generated successfully!")
        for file_path in result.generated_files:
            print(f"  - {file_path}")
    else:
        print("❌ TypeScript generation failed!")


def example_sphinx_only():
    """Generate only Sphinx documentation"""
    print("📚 Example 4: Sphinx Documentation Only")
    
    config = DjangoDocsConfig(
        project_path=Path("/path/to/django/project"),
        project_name="API Documentation"
    )
    
    # Customize Sphinx settings
    config.generation.sphinx_theme_options = {
        "github_url": "https://github.com/myorg/myproject",
        "show_powered_by": False,
        "sidebar_width": "280px"
    }
    config.output.sphinx_output_dir = Path("./docs/api")
    
    generator = DjangoDocsGenerator(str(config.project_path), config=config)
    
    # Generate only Sphinx documentation
    result = generator.generate_sphinx_docs()
    
    if result.success:
        print("📚 Sphinx documentation generated successfully!")
        print("Build with: sphinx-build docs/api docs/api/_build/html")


def example_with_ai_providers():
    """Examples using different AI providers"""
    print("🧠 Example 5: Different AI Providers")
    
    # OpenAI Example
    openai_config = DjangoDocsConfig(project_path=Path("/path/to/project"))
    openai_config.ai.provider = "openai"
    openai_config.ai.model = "gpt-4"
    openai_config.ai.api_key = os.getenv("OPENAI_API_KEY")
    
    # Anthropic Example
    anthropic_config = DjangoDocsConfig(project_path=Path("/path/to/project"))
    anthropic_config.ai.provider = "anthropic"
    anthropic_config.ai.model = "claude-3-sonnet"
    anthropic_config.ai.api_key = os.getenv("ANTHROPIC_API_KEY")
    
    # Local/No AI Example
    local_config = DjangoDocsConfig(project_path=Path("/path/to/project"))
    local_config.ai.provider = "local"  # Disables external AI
    
    # Use the configuration you prefer
    config = openai_config  # or anthropic_config or local_config
    
    generator = DjangoDocsGenerator(str(config.project_path), config=config)
    result = generator.generate_all()
    
    print(f"Generated with {config.ai.provider} provider")


def example_configuration_from_file():
    """Load configuration from TOML file"""
    print("📄 Example 6: Configuration from File")
    
    # Create configuration file path
    config_file = Path("./django_docs_config.toml")
    
    if not config_file.exists():
        print(f"⚠️ Configuration file not found: {config_file}")
        print("Create one using: django-docs-generator init-config django_docs_config.toml")
        return
    
    # Load configuration from file
    config = DjangoDocsConfig.from_file(config_file)
    
    # Override project path if needed
    config.project_path = Path("/path/to/your/project")
    
    generator = DjangoDocsGenerator(str(config.project_path), config=config)
    result = generator.generate_all()
    
    print("Configuration loaded from file successfully!")


def example_error_handling():
    """Demonstrate error handling and validation"""
    print("🛡️ Example 7: Error Handling")
    
    try:
        # Invalid project path
        config = DjangoDocsConfig(project_path=Path("/non/existent/path"))
        generator = DjangoDocsGenerator("/non/existent/path", config=config)
        
        # Validate before generation
        validation_errors = generator.validate_project()
        
        if validation_errors:
            print("❌ Validation errors found:")
            for error in validation_errors:
                print(f"  - {error}")
            return
        
        # This won't be reached due to validation failure
        result = generator.generate_all()
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def example_progressive_generation():
    """Generate documentation progressively (analyze, then generate)"""
    print("🔄 Example 8: Progressive Generation")
    
    config = DjangoDocsConfig(
        project_path=Path("/path/to/django/project"),
        project_name="Progressive API Docs"
    )
    
    generator = DjangoDocsGenerator(str(config.project_path), config=config)
    
    # Step 1: Validate project
    print("1️⃣ Validating project...")
    validation_errors = generator.validate_project()
    if validation_errors:
        print("Validation failed!")
        return
    print("✅ Project validation passed")
    
    # Step 2: Scan project structure
    print("2️⃣ Scanning project structure...")
    scan_result = generator.scanner.scan_project()
    if not scan_result.success:
        print("Project scanning failed!")
        return
    print(f"✅ Found {len(scan_result.discovered_apps)} Django apps")
    
    # Step 3: Generate documentation
    print("3️⃣ Generating documentation...")
    result = generator.generate_all()
    
    print(f"✅ Generated {len(result.generated_files)} files in {result.generation_time:.2f}s")


def example_batch_processing():
    """Process multiple Django projects"""
    print("📦 Example 9: Batch Processing")
    
    django_projects = [
        "/path/to/project1",
        "/path/to/project2",
        "/path/to/project3"
    ]
    
    for i, project_path in enumerate(django_projects, 1):
        print(f"Processing project {i}/{len(django_projects)}: {project_path}")
        
        try:
            config = DjangoDocsConfig(
                project_path=Path(project_path),
                project_name=f"Project {i} API"
            )
            
            # Set unique output directories
            config.output.base_output_dir = Path(f"./docs/project{i}")
            config.output.typescript_output_dir = Path(f"./types/project{i}")
            
            generator = DjangoDocsGenerator(project_path, config=config)
            result = generator.generate_all()
            
            if result.success:
                print(f"  ✅ Project {i} completed successfully")
            else:
                print(f"  ❌ Project {i} failed: {len(result.errors)} errors")
                
        except Exception as e:
            print(f"  💥 Project {i} crashed: {e}")


def example_integration_with_ci():
    """Example suitable for CI/CD integration"""
    print("⚙️ Example 10: CI/CD Integration")
    
    # Get configuration from environment variables
    project_path = os.getenv("DJANGO_PROJECT_PATH", ".")
    output_dir = os.getenv("DOCS_OUTPUT_DIR", "./docs")
    ai_provider = os.getenv("AI_PROVIDER", "local")  # Default to no external AI in CI
    
    config = DjangoDocsConfig(
        project_path=Path(project_path),
        project_name="CI Generated Docs",
        version=os.getenv("PROJECT_VERSION", "1.0.0")
    )
    
    # CI-friendly settings
    config.ai.provider = ai_provider
    config.output.base_output_dir = Path(output_dir)
    config.verbose = os.getenv("VERBOSE", "false").lower() == "true"
    
    generator = DjangoDocsGenerator(project_path, config=config)
    result = generator.generate_all()
    
    # Exit with appropriate code for CI
    exit_code = 0 if result.success else 1
    
    print(f"CI documentation generation {'succeeded' if result.success else 'failed'}")
    print(f"Exit code: {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    """Run all examples (modify paths to your actual Django projects)"""
    
    print("🎯 Django API Documentation Generator - Usage Examples")
    print("=" * 60)
    
    # Note: Update these paths to point to your actual Django projects
    print("⚠️  Please update the project paths in this file before running!")
    print("    Current paths are placeholders: /path/to/your/django/project")
    
    examples = [
        example_basic_usage,
        example_custom_configuration,
        example_typescript_only,
        example_sphinx_only,
        example_with_ai_providers,
        example_configuration_from_file,
        example_error_handling,
        example_progressive_generation,
        # example_batch_processing,  # Uncomment if you have multiple projects
        example_integration_with_ci,
    ]
    
    for example_func in examples:
        try:
            print()
            example_func()
            print("✅ Example completed")
        except Exception as e:
            print(f"❌ Example failed: {e}")
        
        print("-" * 40)