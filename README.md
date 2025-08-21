# Django API Documentation Generator

AI-powered tool that generates comprehensive API documentation and TypeScript interfaces for Django REST Framework projects.

## Installation

```bash
pip install easy-sdk
```

## Quick Start

Generate documentation for the sample e-commerce project:

```bash
# Basic usage - analyze the sample project
easy-sdk sample_projects/ecommerce_api/

# With AI analysis (requires API key)
export OPENAI_API_KEY=sk-your-key-here
easy-sdk sample_projects/ecommerce_api/ --ai-provider openai

# Generate only TypeScript interfaces
easy-sdk sample_projects/ecommerce_api/ --typescript-only

# Generate only Sphinx documentation
easy-sdk sample_projects/ecommerce_api/ --sphinx-only

# Specify output directory
easy-sdk sample_projects/ecommerce_api/ --output-dir ./generated_docs
```

## What it generates

**Sphinx Documentation:**
- Complete API reference organized by Django apps
- Endpoint documentation with request/response examples
- Model and serializer field documentation

**TypeScript Interfaces:**
- Accurate type definitions for all API endpoints
- Input/output types for each serializer
- Properly typed request/response objects

## Example Output Structure

```
generated_docs/
├── sphinx/
│   ├── index.rst
│   ├── apps/
│   │   ├── products/
│   │   │   ├── models.rst
│   │   │   ├── serializers.rst
│   │   │   └── endpoints.rst
│   │   ├── orders/
│   │   └── users/
│   └── _build/html/  # Generated HTML docs
└── typescript/
    ├── products.d.ts
    ├── orders.d.ts
    ├── users.d.ts
    └── index.d.ts
```

## AI Configuration

Set environment variables for AI providers:

```bash
# OpenAI
export OPENAI_API_KEY=sk-your-openai-key

# Anthropic
export ANTHROPIC_API_KEY=sk-ant-your-key

# Then use with AI
easy-sdk sample_projects/ecommerce_api/ --ai-provider openai --ai-model gpt-4
```

## CLI Options

```bash
easy-sdk --help

Options:
  --output-dir, -o PATH      Output directory (default: ./docs)
  --apps, -a TEXT           Include specific apps only
  --typescript-only         Generate only TypeScript definitions
  --sphinx-only            Generate only Sphinx documentation
  --ai-provider TEXT       AI provider: openai, anthropic, local
  --ai-model TEXT          AI model (e.g., gpt-4, claude-3-sonnet)
  --no-ai                  Disable AI analysis
  --config, -c PATH        Configuration file
  --verbose, -v            Verbose output
  --help                   Show this help message
```

## Configuration File

Create `django_docs_config.toml`:

```toml
[project]
name = "E-commerce API"
version = "1.0.0"

[apps]
include = ["products", "orders", "users"]

[ai]
provider = "openai"
model = "gpt-4"

[output]
base_output_dir = "./docs"
typescript_output_dir = "./frontend/types"
```

## Development

```bash
git clone https://github.com/your-org/easy-sdk.git
cd easy-sdk
pip install -e .[dev]
pytest
```