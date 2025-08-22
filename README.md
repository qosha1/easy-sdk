# Easy SDK - Django API Documentation & SDK Generator

🚀 **AI-powered tool that generates comprehensive API documentation and client SDKs for Django REST Framework projects.**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/your-org/easy-sdk)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/django-3.2+-green.svg)](https://djangoproject.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## ✨ What Easy SDK Does

Easy SDK transforms your Django REST Framework projects into:

- **📚 Interactive Documentation** - Beautiful Swagger-like docs with live API testing
- **🐍 Python SDKs** - Complete async client libraries with type hints and Pydantic models  
- **🔷 TypeScript SDKs** - Full-featured clients with comprehensive type definitions
- **🤖 AI-Enhanced** - Smart structure analysis and code generation using OpenAI/Anthropic

## 🚀 Quick Start

### Installation

```bash
pip install easy-sdk
```

### Generate Everything

```bash
# Generate interactive docs + Python & TypeScript SDKs
easy-sdk /path/to/django/project generate-sdk --language python --language typescript

# Or generate just documentation
easy-sdk /path/to/django/project --format docusaurus
```

## 📖 Documentation Generation

### Docusaurus (Interactive Documentation)

Generate beautiful, interactive API documentation with live testing capabilities:

```bash
# Generate Docusaurus documentation
easy-sdk /path/to/project --format docusaurus

# The generated docs include:
# - Interactive Swagger-like API explorer
# - Live API testing in the browser
# - Auto-generated request/response examples
# - Beautiful, responsive UI
```

**Features:**
- 🧪 **Interactive Testing** - Test APIs directly in the browser
- 📊 **Schema Visualization** - Expandable object schemas
- 🎨 **Modern UI** - Clean, Swagger-style interface
- 🔧 **Auto-deployment** - Works with any existing Docusaurus project

### Sphinx (Traditional Documentation)

```bash
# Generate traditional Sphinx documentation
easy-sdk /path/to/project --format sphinx
```

## 🛠 SDK Generation

Easy SDK generates production-ready client libraries for multiple programming languages.

### Python SDKs

```bash
easy-sdk /path/to/project generate-sdk --language python --library-name "my_api_client"
```

**Generated Python SDK features:**
- ✅ **Async/await support** - Modern asynchronous HTTP client
- ✅ **Type hints** - Full type safety with Pydantic models
- ✅ **Error handling** - Comprehensive exception hierarchy
- ✅ **Auto-retry** - Exponential backoff for failed requests
- ✅ **Authentication** - Token, Bearer, JWT support
- ✅ **Validation** - Request/response validation with Pydantic

**Example usage:**
```python
import asyncio
from my_api_client import MyApiClient

async def main():
    async with MyApiClient(api_key="your-key") as client:
        # List users
        users = await client.users.list_users()
        
        # Create user
        user = await client.users.create_user({
            "name": "John Doe",
            "email": "john@example.com"
        })
        
        # Get user details
        user_details = await client.users.get_user(user["id"])

asyncio.run(main())
```

### TypeScript SDKs

```bash
easy-sdk /path/to/project generate-sdk --language typescript --library-name "my-api-client"
```

**Generated TypeScript SDK features:**
- ✅ **Full type definitions** - Complete TypeScript interfaces
- ✅ **Modern async/await** - Promise-based API
- ✅ **Browser + Node.js** - Universal compatibility
- ✅ **Tree-shakable** - ESM and CommonJS support
- ✅ **Auto-retry** - Built-in retry logic with backoff
- ✅ **Type-safe** - Compile-time API validation

**Example usage:**
```typescript
import { MyApiClient } from 'my-api-client';

const client = new MyApiClient({
  apiKey: 'your-key',
  baseUrl: 'https://api.example.com'
});

// Fully typed responses
const users: User[] = await client.users.listUsers();

// Type-safe requests
const newUser: User = await client.users.createUser({
  name: 'John Doe',
  email: 'john@example.com'
});
```

### Multi-Language Generation

```bash
# Generate both Python and TypeScript SDKs
easy-sdk /path/to/project generate-sdk \
  --language python \
  --language typescript \
  --library-name "awesome_api"
```

## 🤖 AI-Powered Features

Easy SDK uses AI to intelligently analyze your Django project and generate optimal code structures.

### Setup AI Integration

```bash
# OpenAI (GPT-4, GPT-3.5)
export OPENAI_API_KEY=sk-your-openai-key

# Anthropic (Claude)
export ANTHROPIC_API_KEY=sk-ant-your-key

# Use AI for enhanced generation
easy-sdk /path/to/project generate-sdk \
  --language python \
  --ai-provider openai \
  --ai-model gpt-4
```

**AI enhancements include:**
- 📊 **Smart API Analysis** - Identifies patterns and optimal SDK structure
- 🏗 **Architecture Recommendations** - Suggests best practices for client organization  
- 🔍 **Error Pattern Detection** - Improves error handling based on API patterns
- 📝 **Enhanced Documentation** - Generates better descriptions and examples

## 📋 Commands Reference

### Main Commands

```bash
# Generate documentation
easy-sdk /path/to/project [OPTIONS]

# Generate client SDKs  
easy-sdk /path/to/project generate-sdk [OPTIONS]

# List supported SDK languages
easy-sdk list-sdk-languages

# Analyze project structure
easy-sdk /path/to/project analyze

# Validate Django project
easy-sdk /path/to/project validate
```

### SDK Generation Options

```bash
--language, -l          SDK language(s): python, typescript, js, ts
--library-name          Custom library name
--output-dir, -o        Output directory
--preview-only          Preview structure without generating
--ai-provider           AI provider: openai, anthropic, local
--ai-model             AI model (e.g., gpt-4, claude-3)
--apps, -a             Include specific Django apps
--verbose, -v          Enable verbose logging
```

### Documentation Options

```bash
--format, -f           Format: sphinx, docusaurus
--output-dir, -o       Output directory
--docusaurus-only      Generate only Docusaurus docs
--sphinx-only          Generate only Sphinx docs  
--apps, -a             Include specific Django apps
--ai-provider          AI provider for enhanced docs
```

## 📁 Generated Structure

### SDK Output Structure

**Python SDK:**
```
sdk_python/
├── setup.py                    # Package setup
├── requirements.txt            # Dependencies  
├── my_api_client/
│   ├── __init__.py            # Main exports
│   ├── client.py              # Main SDK client
│   ├── base_client.py         # HTTP client base
│   ├── exceptions.py          # Error handling
│   ├── models/                # Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── product.py
│   └── clients/               # App-specific clients
│       ├── users_client.py
│       └── products_client.py
```

**TypeScript SDK:**
```
sdk_typescript/
├── package.json               # Package configuration
├── tsconfig.json             # TypeScript config
├── src/
│   ├── index.ts              # Main exports
│   ├── BaseClient.ts         # HTTP client
│   ├── exceptions.ts         # Error classes
│   ├── types/                # Type definitions
│   │   ├── index.ts
│   │   ├── common.ts
│   │   ├── users.ts
│   │   └── products.ts
│   └── clients/              # API clients
│       ├── UsersClient.ts
│       └── ProductsClient.ts
```

### Documentation Structure

**Docusaurus:**
```
docusaurus/
├── docs/
│   ├── intro.md
│   └── api/
│       ├── users/
│       │   ├── index.md       # Interactive API explorer
│       │   └── endpoints.md   # Detailed endpoints
│       └── products/
├── src/
│   └── components/           # React components
│       ├── ApiExplorer/      # Interactive API testing
│       └── SwaggerApiDocs/   # Swagger-like UI
├── docusaurus.config.js
└── package.json
```

## ⚙️ Configuration

Create `.easy-sdk.toml` in your project root:

```toml
[project]
name = "My API"
version = "1.0.0"

[generation]
documentation_format = "docusaurus"  # or "sphinx"
language_template = "typescript"
generate_multiple_languages = true
additional_languages = ["python"]

[output]
base_output_dir = "./generated"
sphinx_output_dir = "./docs"

[ai]
provider = "openai"  # or "anthropic"
model = "gpt-4"
temperature = 0.1

[apps]
include_apps = ["users", "products", "orders"]
exclude_apps = ["admin", "internal"]
```

## 🎯 Real-World Examples

### E-commerce API

```bash
# Generate complete SDK suite for e-commerce API
easy-sdk /path/to/ecommerce generate-sdk \
  --language python \
  --language typescript \
  --library-name "ecommerce-sdk" \
  --ai-provider openai
```

### SaaS Platform API

```bash  
# Generate interactive docs + Python SDK
easy-sdk /path/to/saas-api generate-sdk \
  --language python \
  --library-name "saas_client" \
  --apps users subscriptions billing \
  --format docusaurus
```

## 🔧 Advanced Features

### Preview Mode
```bash
# Preview SDK structure without generating files
easy-sdk /path/to/project generate-sdk --preview-only --language python
```

### Custom Templates
```bash
# Use custom naming conventions
easy-sdk /path/to/project generate-sdk \
  --language typescript \
  --interface-naming PascalCase \
  --property-naming camelCase
```

### Selective Generation
```bash
# Generate only specific Django apps
easy-sdk /path/to/project generate-sdk \
  --language python \
  --apps users products \
  --exclude-apps admin
```

## 🚦 Requirements

- **Python 3.8+**
- **Django 3.2+** 
- **Django REST Framework 3.12+**

### Optional Dependencies

```bash
# For AI features
pip install easy-sdk[ai]

# For development
pip install easy-sdk[dev]
```

## 📈 Supported Languages

| Language   | Status | Features |
|------------|--------|----------|
| Python     | ✅ Full | Async, Type Hints, Pydantic |
| TypeScript | ✅ Full | Full Types, ESM/CommonJS |
| JavaScript | ✅ Full | Same as TypeScript |

## 🤝 Contributing

```bash
git clone https://github.com/your-org/easy-sdk.git
cd easy-sdk
pip install -e .[dev]
pytest
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

## 🙋‍♀️ Support

- **Issues**: [GitHub Issues](https://github.com/your-org/easy-sdk/issues)
- **Documentation**: [Full Documentation](https://docs.easy-sdk.dev)
- **Examples**: See `sample_projects/` directory

---

**Made with ❤️ for Django developers who want to ship great APIs faster.**