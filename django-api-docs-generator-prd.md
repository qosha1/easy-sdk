# Product Requirements Document: Django API Documentation Generator

## Product Overview

### Product Name
Django API Docs Generator with AI-Powered Analysis

### Vision Statement
An intelligent Python library that automatically generates comprehensive API documentation for Django backend repositories by leveraging AI and structural code analysis to understand serializers, endpoints, and data flows.

### Target Users
- Django developers and development teams
- Technical writers and documentation maintainers
- DevOps engineers managing API documentation
- Frontend developers consuming Django APIs

## Product Objectives

### Primary Goals
1. **Automated Documentation Generation**: Eliminate manual API documentation creation and maintenance
2. **Intelligent Analysis**: Use AI to understand code structure, relationships, and data flows
3. **Developer Experience**: Provide TypeScript interfaces for seamless frontend integration
4. **Documentation Quality**: Generate Sphinx-compatible documentation with proper categorization

### Success Metrics
- Reduce API documentation creation time by 90%
- Achieve 95% accuracy in serializer analysis and type inference
- Support for 100% of Django REST Framework serializer types
- Generate TypeScript interfaces with <5% manual correction needed

## Technical Requirements

### Core Functionality

#### Django Repository Analysis
- **Repository Scanning**: Recursively analyze Django project structure
- **App Discovery**: Automatically identify Django apps and their boundaries
- **URL Pattern Analysis**: Parse URL configurations to identify API endpoints
- **View Function Analysis**: Extract view classes, methods, and decorators
- **Serializer Detection**: Identify and analyze DRF serializers and their fields

#### AI-Powered Structural Analysis
- **Code Understanding**: Use LLM to interpret complex serializer logic
- **Relationship Mapping**: Identify relationships between models, serializers, and views
- **Type Inference**: Determine input/output types from serializer definitions
- **Documentation Extraction**: Parse docstrings, comments, and inline documentation
- **Validation Logic Analysis**: Understand custom validation and field requirements

#### Sphinx Documentation Generation
- **Sphinx 6.2.1 Compatibility**: Generate reStructuredText files compatible with Sphinx 6.2.1
- **Alabaster 0.7.16 Theme**: Ensure proper rendering with Alabaster theme
- **App-based Organization**: Structure documentation by Django apps
- **Endpoint Categorization**: Group endpoints logically (CRUD operations, authentication, etc.)
- **Interactive Examples**: Include request/response examples for each endpoint

#### TypeScript Interface Generation
- **Type Mapping**: Convert Python/Django types to TypeScript equivalents
- **Nested Object Support**: Handle complex nested serializer structures
- **Optional Fields**: Properly mark optional vs required fields
- **Union Types**: Support for choice fields and polymorphic serializers
- **Generic Types**: Handle generic serializers and list responses

### Technical Specifications

#### Input Requirements
- Django project directory path
- Python environment with Django and DRF installed
- Optional: Configuration file for customization

#### Output Deliverables
1. **Sphinx Documentation Files**
   - `index.rst`: Main documentation index
   - `apps/<app_name>/index.rst`: Per-app documentation
   - `apps/<app_name>/endpoints.rst`: Endpoint documentation per app
   - `_static/`: Static assets and custom CSS

2. **TypeScript Declaration Files**
   - `types/<app_name>.d.ts`: Type definitions per Django app
   - `types/index.d.ts`: Consolidated type exports
   - `types/common.d.ts`: Shared types and utilities

3. **Documentation Assets**
   - OpenAPI/Swagger JSON specification
   - Postman collection export
   - Example request/response payloads

#### Supported Django/DRF Features
- **Serializers**: ModelSerializer, Serializer, ListSerializer, nested serializers
- **Fields**: All standard DRF field types, custom fields, method fields
- **Views**: APIView, ViewSet, ModelViewSet, generic views
- **Authentication**: Token, Session, JWT, custom authentication
- **Permissions**: Built-in and custom permission classes
- **Filtering**: django-filter, custom filtering, search
- **Pagination**: Built-in pagination classes

## Architecture and Implementation

### High-Level Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Django Repo   │───▶│  Code Analyzer   │───▶│   AI Engine     │
│   Scanner       │    │   & Parser       │    │  (LLM Integration)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Sphinx        │    │  TypeScript      │    │  Configuration  │
│   Generator     │    │  Generator       │    │  & Templates    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Core Components

#### 1. Repository Scanner
- **File Discovery**: Locate Python files, URL configurations, settings
- **Import Analysis**: Build dependency graph of imports and references
- **AST Parsing**: Parse Python files into Abstract Syntax Trees

#### 2. Code Analyzer
- **Serializer Parser**: Extract field definitions, validators, and metadata
- **View Analyzer**: Identify HTTP methods, permissions, and response handling
- **URL Mapper**: Map URL patterns to view functions/classes

#### 3. AI Engine Integration
- **Context Building**: Prepare code context for LLM analysis
- **Type Inference**: Use AI to determine complex type relationships
- **Documentation Enhancement**: Generate human-readable descriptions

#### 4. Documentation Generators
- **Sphinx Generator**: Create reStructuredText files with proper formatting
- **TypeScript Generator**: Generate accurate type definitions
- **Template Engine**: Use Jinja2 templates for consistent output

### Configuration Options

#### Basic Configuration
```python
# django_docs_config.py
DJANGO_DOCS_CONFIG = {
    'project_name': 'My Django API',
    'version': '1.0.0',
    'description': 'Auto-generated API documentation',
    'include_apps': ['api', 'users', 'products'],  # Optional: specific apps only
    'exclude_endpoints': ['/admin/', '/debug/'],
    'typescript_output_dir': './frontend/src/types/',
    'sphinx_output_dir': './docs/api/',
}
```

#### Advanced Configuration
```python
AI_CONFIG = {
    'provider': 'openai',  # or 'anthropic', 'local'
    'model': 'gpt-4',
    'max_tokens': 4000,
    'temperature': 0.1,
}

GENERATION_CONFIG = {
    'include_examples': True,
    'generate_postman_collection': True,
    'include_internal_endpoints': False,
    'typescript_strict_mode': True,
    'sphinx_theme_options': {
        'github_url': 'https://github.com/myorg/myproject',
        'show_powered_by': False,
    }
}
```

## Usage Examples

### Command Line Interface
```bash
# Basic usage
django-docs-generator /path/to/django/project

# With custom config
django-docs-generator /path/to/project --config django_docs_config.py

# Specific apps only
django-docs-generator /path/to/project --apps api users products

# Output to specific directory
django-docs-generator /path/to/project --output-dir ./custom-docs/
```

### Python API
```python
from django_docs_generator import DjangoDocsGenerator

generator = DjangoDocsGenerator(
    project_path='/path/to/django/project',
    config_path='./django_docs_config.py'
)

# Generate all documentation
generator.generate_all()

# Generate only TypeScript types
generator.generate_typescript_types()

# Generate only Sphinx docs
generator.generate_sphinx_docs()
```

## Dependencies and Requirements

### Python Dependencies
- Python 3.8+
- Django 3.2+
- Django REST Framework 3.12+
- Sphinx 6.2.1
- Jinja2 3.1+
- AST analysis libraries (ast, astroid)
- AI/LLM client libraries (openai, anthropic, or local inference)

### Optional Dependencies
- django-filter (for filtering documentation)
- djangorestframework-simplejwt (for JWT auth documentation)
- drf-spectacular (for OpenAPI integration)

## Deliverables and Timeline

### Phase 1: Core Analysis Engine (4 weeks)
- Django repository scanner
- Basic serializer analysis
- URL pattern mapping
- Simple Sphinx output generation

### Phase 2: AI Integration (3 weeks)
- LLM integration for code understanding
- Enhanced type inference
- Automatic documentation generation
- Complex serializer relationship analysis

### Phase 3: TypeScript Generation (2 weeks)
- TypeScript interface generation
- Type mapping accuracy improvements
- Support for complex nested structures
- Integration with popular frontend frameworks

### Phase 4: Documentation Enhancement (2 weeks)
- Advanced Sphinx features
- Custom templates and themes
- Interactive examples
- Postman collection generation

### Phase 5: Testing and Polish (2 weeks)
- Comprehensive testing suite
- Performance optimization
- CLI improvements
- Documentation and tutorials

## Risk Assessment

### Technical Risks
1. **Complex Serializer Logic**: Some serializers may have complex validation logic that's difficult to analyze
2. **Custom Field Types**: Custom serializer fields might not be properly recognized
3. **Dynamic URL Patterns**: Runtime-generated URL patterns may be missed
4. **AI Accuracy**: LLM analysis might misinterpret code context

### Mitigation Strategies
1. Provide fallback analysis methods for complex cases
2. Allow manual annotation/hints for custom fields
3. Support configuration-based URL pattern specification
4. Implement validation and review mechanisms for AI-generated content

## Success Criteria

### Functional Requirements
- [ ] Successfully analyze 95% of Django apps without configuration
- [ ] Generate accurate TypeScript interfaces for all standard DRF field types
- [ ] Produce Sphinx documentation that renders correctly with Alabaster theme
- [ ] Support Django 3.2+ and DRF 3.12+ compatibility
- [ ] Process medium-sized Django projects (50+ endpoints) within 5 minutes

### Quality Requirements
- [ ] Generated TypeScript compiles without errors
- [ ] Sphinx documentation builds without warnings
- [ ] API examples are syntactically correct and runnable
- [ ] Documentation includes proper cross-references and navigation

This PRD provides a comprehensive foundation for building an AI-powered Django API documentation generator that meets the specified requirements for Sphinx integration and TypeScript interface generation.