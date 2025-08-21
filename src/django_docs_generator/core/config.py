"""
Configuration management for Django API Documentation Generator
"""

import os
import tomllib
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class AIConfig(BaseModel):
    """Configuration for AI/LLM integration"""
    
    provider: str = Field(default="openai", description="AI provider: openai, anthropic, or local")
    model: str = Field(default="gpt-4", description="Model name to use")
    api_key: Optional[str] = Field(default=None, description="API key for the provider")
    max_tokens: int = Field(default=4000, description="Maximum tokens for AI responses")
    temperature: float = Field(default=0.1, description="Temperature for AI generation")
    timeout: int = Field(default=60, description="Request timeout in seconds")
    
    @validator('provider')
    def validate_provider(cls, v):
        valid_providers = ['openai', 'anthropic', 'local']
        if v not in valid_providers:
            raise ValueError(f"Provider must be one of: {valid_providers}")
        return v
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0 <= v <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        return v


class GenerationConfig(BaseModel):
    """Configuration for documentation generation"""
    
    include_examples: bool = Field(default=True, description="Include request/response examples")
    generate_postman_collection: bool = Field(default=True, description="Generate Postman collection")
    include_internal_endpoints: bool = Field(default=False, description="Include internal/admin endpoints")
    typescript_strict_mode: bool = Field(default=True, description="Generate strict TypeScript types")
    max_depth: int = Field(default=10, description="Maximum nesting depth for serializers")
    
    # Sphinx-specific options
    sphinx_theme_options: Dict[str, Any] = Field(
        default_factory=lambda: {
            "github_url": "",
            "show_powered_by": False,
            "sidebar_width": "240px",
        }
    )


class OutputConfig(BaseModel):
    """Configuration for output directories and files"""
    
    base_output_dir: Path = Field(default=Path("./docs"), description="Base output directory")
    sphinx_output_dir: Path = Field(default=Path("./docs/api"), description="Sphinx documentation output")
    typescript_output_dir: Path = Field(default=Path("./types"), description="TypeScript types output")
    static_output_dir: Path = Field(default=Path("./docs/_static"), description="Static assets output")
    
    # File naming patterns
    typescript_filename_pattern: str = Field(default="{app_name}.d.ts", description="TypeScript file naming")
    sphinx_filename_pattern: str = Field(default="{app_name}.rst", description="Sphinx file naming")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Convert string paths to Path objects
        for field_name, field in self.__fields__.items():
            if field.type_ == Path:
                value = getattr(self, field_name)
                if isinstance(value, str):
                    setattr(self, field_name, Path(value))


class DjangoDocsConfig(BaseModel):
    """Main configuration class for Django API Documentation Generator"""
    
    # Project information
    project_name: str = Field(default="Django API", description="Project name for documentation")
    version: str = Field(default="1.0.0", description="Project version")
    description: str = Field(default="Auto-generated API documentation", description="Project description")
    author: str = Field(default="", description="Documentation author")
    
    # Django project settings
    project_path: Path = Field(..., description="Path to Django project root")
    django_settings_module: Optional[str] = Field(default=None, description="Django settings module")
    
    # App filtering
    include_apps: Optional[List[str]] = Field(default=None, description="Specific apps to include")
    exclude_apps: List[str] = Field(default_factory=list, description="Apps to exclude")
    exclude_endpoints: List[str] = Field(
        default_factory=lambda: ["/admin/", "/debug/"], 
        description="Endpoint patterns to exclude"
    )
    
    # Sub-configurations
    ai: AIConfig = Field(default_factory=AIConfig)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    
    # Advanced options
    verbose: bool = Field(default=False, description="Enable verbose logging")
    dry_run: bool = Field(default=False, description="Perform dry run without generating files")
    parallel_processing: bool = Field(default=True, description="Enable parallel processing")
    max_workers: int = Field(default=4, description="Maximum number of worker threads")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Ensure project_path is absolute
        if not self.project_path.is_absolute():
            self.project_path = Path.cwd() / self.project_path
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> "DjangoDocsConfig":
        """Load configuration from a TOML file"""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        if config_path.suffix == '.toml':
            with open(config_path, 'rb') as f:
                config_data = tomllib.load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
        
        return cls(**config_data)
    
    @classmethod
    def from_django_settings(cls, project_path: Union[str, Path]) -> "DjangoDocsConfig":
        """Load configuration from Django settings if available"""
        project_path = Path(project_path)
        
        # Try to import Django settings
        try:
            import django
            from django.conf import settings
            
            if hasattr(settings, 'DJANGO_DOCS_CONFIG'):
                config_data = settings.DJANGO_DOCS_CONFIG
                config_data['project_path'] = project_path
                return cls(**config_data)
        except ImportError:
            pass
        
        # Return default configuration
        return cls(project_path=project_path)
    
    def create_output_directories(self) -> None:
        """Create all configured output directories"""
        directories = [
            self.output.base_output_dir,
            self.output.sphinx_output_dir,
            self.output.typescript_output_dir,
            self.output.static_output_dir,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_app_output_path(self, app_name: str, output_type: str) -> Path:
        """Get output path for a specific app and output type"""
        if output_type == "sphinx":
            filename = self.output.sphinx_filename_pattern.format(app_name=app_name)
            return self.output.sphinx_output_dir / "apps" / app_name / filename
        elif output_type == "typescript":
            filename = self.output.typescript_filename_pattern.format(app_name=app_name)
            return self.output.typescript_output_dir / filename
        else:
            raise ValueError(f"Unknown output type: {output_type}")
    
    def should_include_app(self, app_name: str) -> bool:
        """Check if an app should be included in documentation generation"""
        if self.include_apps is not None and app_name not in self.include_apps:
            return False
        
        if app_name in self.exclude_apps:
            return False
        
        return True
    
    def should_include_endpoint(self, endpoint_path: str) -> bool:
        """Check if an endpoint should be included in documentation"""
        for exclude_pattern in self.exclude_endpoints:
            if exclude_pattern in endpoint_path:
                return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return self.dict()
    
    def save_to_file(self, config_path: Union[str, Path]) -> None:
        """Save configuration to a TOML file"""
        config_path = Path(config_path)
        
        # Convert to dictionary and handle Path objects
        config_dict = self.dict()
        self._convert_paths_to_strings(config_dict)
        
        if config_path.suffix == '.toml':
            import tomli_w
            with open(config_path, 'wb') as f:
                tomli_w.dump(config_dict, f)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
    
    def _convert_paths_to_strings(self, data: Any) -> None:
        """Recursively convert Path objects to strings in a dictionary"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, Path):
                    data[key] = str(value)
                elif isinstance(value, (dict, list)):
                    self._convert_paths_to_strings(value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, Path):
                    data[i] = str(item)
                elif isinstance(item, (dict, list)):
                    self._convert_paths_to_strings(item)


# Default configuration instance
DEFAULT_CONFIG = DjangoDocsConfig(project_path=Path.cwd())