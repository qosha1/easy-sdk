# Django API Documentation Generator

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Django 3.2+](https://img.shields.io/badge/django-3.2+-green.svg)](https://www.djangoproject.com/)
[![DRF 3.12+](https://img.shields.io/badge/drf-3.12+-orange.svg)](https://www.django-rest-framework.org/)

An intelligent Python library that automatically generates comprehensive API documentation for Django backend repositories by leveraging AI and structural code analysis to understand serializers, endpoints, and data flows.

## 🚀 Features

- **🔍 Intelligent Analysis**: Uses AI to understand complex serializer logic and relationships
- **📚 Sphinx Documentation**: Generates beautiful, Sphinx 6.2.1 compatible documentation with Alabaster theme
- **📝 TypeScript Interfaces**: Creates accurate TypeScript type definitions for all API endpoints
- **🎯 App-based Organization**: Structures documentation by Django apps, similar to Swagger
- **⚡ CLI & Python API**: Use via command line or integrate into your Python workflow
- **🤖 AI-Powered**: Supports OpenAI, Anthropic, and local AI models for enhanced analysis
- **🔧 Highly Configurable**: Extensive configuration options for customization

## 📦 Installation

```bash
pip install django-api-docs-generator
```

### Development Installation

```bash
git clone https://github.com/django-docs-generator/django-api-docs-generator.git
cd django-api-docs-generator
pip install -e .
```

## 🏃‍♂️ Quick Start

### Command Line Usage

```bash
# Basic usage - analyze current directory
django-docs-generator /path/to/django/project

# Generate with custom configuration
django-docs-generator /path/to/project --config config.toml

# Generate only TypeScript definitions
django-docs-generator /path/to/project --typescript-only

# Generate only Sphinx documentation
django-docs-generator /path/to/project --sphinx-only

# Specify output directory
django-docs-generator /path/to/project --output-dir ./docs

# Include specific apps only
django-docs-generator /path/to/project --apps api users products

# Use different AI provider
django-docs-generator /path/to/project --ai-provider anthropic --ai-model claude-3
```

### Python API Usage

```python
from django_docs_generator import DjangoDocsGenerator

# Basic usage
generator = DjangoDocsGenerator(
    project_path='/path/to/django/project'
)

# Generate all documentation
result = generator.generate_all()

if result.success:
    print(f"✅ Generated {len(result.generated_files)} files")
    print(f"📁 Output directory: {generator.config.output.base_output_dir}")
else:
    print("❌ Generation failed:")
    for error in result.errors:
        print(f"  - {error}")
```

### Configuration File

Create a `django_docs_config.toml` file:

```toml
[project]
name = "My Django API"
version = "1.0.0"
description = "Auto-generated API documentation"
author = "Your Name"

[apps]
include = ["api", "users", "products"]  # Optional: specific apps only
exclude = ["admin", "debug"]            # Apps to exclude

[ai]
provider = "openai"  # or "anthropic", "local"
model = "gpt-4"
max_tokens = 4000
temperature = 0.1

[generation]
include_examples = true
generate_postman_collection = true
typescript_strict_mode = true

[output]
base_output_dir = "./docs"
sphinx_output_dir = "./docs/api"
typescript_output_dir = "./frontend/src/types"

[output.sphinx_theme_options]
github_url = "https://github.com/myorg/myproject"
show_powered_by = false
```

## 🎯 Use Cases

### Frontend Development

Generate TypeScript interfaces for seamless frontend integration:

```typescript
// Generated types are ready to use
import { User, CreateUserRequest, UserResponse } from './types';

const createUser = async (userData: CreateUserRequest): Promise<UserResponse> => {
  const response = await fetch('/api/users/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData)
  });
  return response.json();
};
```

### API Documentation

Automatically generated Sphinx documentation includes:

- **Endpoint Documentation**: Complete REST API reference
- **Serializer Reference**: Field types, validation rules, examples
- **Model Documentation**: Database schema and relationships
- **Interactive Examples**: Copy-paste ready code samples

### CI/CD Integration

```yaml
# .github/workflows/docs.yml
name: Generate API Documentation

on:
  push:
    branches: [ main ]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install django-api-docs-generator
    
    - name: Generate documentation
      run: |
        django-docs-generator . --output-dir ./docs
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./docs
```

## 🔧 Advanced Configuration

### Custom AI Configuration

```python
from django_docs_generator import DjangoDocsGenerator, DjangoDocsConfig

config = DjangoDocsConfig(
    project_path="/path/to/project",
    project_name="Advanced API",
)

# Configure AI settings
config.ai.provider = "anthropic"
config.ai.model = "claude-3-sonnet"
config.ai.api_key = "your-api-key"  # or set ANTHROPIC_API_KEY env var
config.ai.max_tokens = 8000
config.ai.temperature = 0.2

generator = DjangoDocsGenerator("/path/to/project", config=config)
result = generator.generate_all()
```

### Custom Output Formatting

```python
# Customize TypeScript generation
config.generation.typescript_strict_mode = True
config.output.typescript_filename_pattern = "{app_name}-types.d.ts"

# Customize Sphinx generation
config.generation.sphinx_theme_options = {
    "github_url": "https://github.com/myorg/myproject",
    "show_powered_by": False,
    "sidebar_width": "280px",
    "page_width": "1200px"
}
```

## 🧠 AI-Powered Features

The library uses AI to enhance code understanding:

### Intelligent Type Inference

- Analyzes complex serializer validation logic
- Infers TypeScript types from Django field constraints
- Understands relationships between models and serializers

### Enhanced Documentation

- Generates human-readable descriptions from code
- Creates realistic API usage examples
- Explains business logic and validation rules

### Relationship Mapping

- Identifies dependencies between components
- Maps data flow through serializers and views
- Detects circular dependencies

## 📋 Supported Features

### Django/DRF Compatibility

- ✅ Django 3.2+ and Django REST Framework 3.12+
- ✅ All standard DRF serializers and fields
- ✅ Custom serializers and nested relationships
- ✅ ViewSets, APIViews, and generic views
- ✅ Authentication and permission classes
- ✅ Filtering, searching, and pagination
- ✅ Custom actions and decorators

### Generated Output

**Sphinx Documentation:**
- `index.rst`: Main documentation index
- `apps/<app>/`: Per-app documentation
- `_static/`: Custom CSS and JavaScript
- Interactive API examples

**TypeScript Types:**
- `types/<app>.d.ts`: App-specific type definitions
- `types/common.d.ts`: Shared utility types
- `types/index.d.ts`: Main export file

## 🔍 CLI Commands

### Generate Documentation

```bash
# Full generation
django-docs-generator /path/to/project

# Analyze only (no file generation)
django-docs-generator analyze /path/to/project

# Validate project compatibility
django-docs-generator validate /path/to/project

# Initialize configuration file
django-docs-generator init-config ./django_docs_config.toml
```

### CLI Options

```bash
django-docs-generator --help

Options:
  --config, -c PATH          Configuration file path
  --output-dir, -o PATH      Output directory
  --apps, -a TEXT            Specific apps to include
  --exclude-apps TEXT        Apps to exclude
  --verbose, -v              Enable verbose logging
  --dry-run                  Analyze without generating files
  --typescript-only          Generate only TypeScript
  --sphinx-only              Generate only Sphinx docs
  --ai-provider TEXT         AI provider (openai/anthropic/local)
  --ai-model TEXT            AI model name
  --no-ai                    Disable AI analysis
  --version                  Show version
  --help                     Show help message
```

## 🏗️ Architecture

The library consists of several key components:

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

### Component Overview

- **Django Scanner**: Discovers apps, models, views, serializers
- **Code Analyzer**: Parses Python AST and extracts metadata
- **AI Engine**: Enhances analysis with intelligent understanding
- **Generators**: Create Sphinx docs and TypeScript definitions
- **CLI**: Command-line interface with rich output

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/django-docs-generator/django-api-docs-generator.git
cd django-api-docs-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=src/django_docs_generator

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django and Django REST Framework communities
- OpenAI and Anthropic for AI capabilities
- Sphinx documentation system
- All contributors and users of this library

## 📞 Support

- 📖 [Documentation](https://django-api-docs-generator.readthedocs.io)
- 🐛 [Issue Tracker](https://github.com/django-docs-generator/django-api-docs-generator/issues)
- 💬 [Discussions](https://github.com/django-docs-generator/django-api-docs-generator/discussions)

---

**Made with ❤️ for the Django community**