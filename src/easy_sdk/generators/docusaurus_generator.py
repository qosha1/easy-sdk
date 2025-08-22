"""
Docusaurus documentation generator for Django API documentation
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.config import DjangoDocsConfig

logger = logging.getLogger(__name__)


class DocusaurusGenerator:
    """
    Generates Docusaurus 3.x compatible documentation from Django analysis results.
    Can either create new documentation or extend existing Docusaurus setups.
    """
    
    def __init__(self, config: DjangoDocsConfig):
        self.config = config
        self.output_dir = config.output.docusaurus_output_dir if hasattr(config.output, 'docusaurus_output_dir') else config.output.base_output_dir / "docusaurus"
        self.is_existing_docusaurus = self._detect_existing_docusaurus()
        self.easy_sdk_section = "easy_sdk"
        
    def generate_documentation(self, analysis_result: Optional[Dict[str, Any]] = None) -> List[Path]:
        """
        Generate complete Docusaurus documentation
        
        Args:
            analysis_result: Analysis results from Django components
        
        Returns:
            List of generated file paths
        """
        generated_files = []
        
        try:
            # Create Docusaurus project structure
            self._create_directory_structure()
            
            # Generate configuration files
            config_files = self._generate_config_files()
            generated_files.extend(config_files)
            
            # Generate documentation content
            if analysis_result:
                content_files = self._generate_content(analysis_result)
                generated_files.extend(content_files)
            
            # Generate package.json and setup files
            setup_files = self._generate_setup_files()
            generated_files.extend(setup_files)
            
            logger.info(f"Generated {len(generated_files)} Docusaurus documentation files")
            
        except Exception as e:
            logger.error(f"Failed to generate Docusaurus documentation: {str(e)}")
        
        return generated_files
    
    def _detect_existing_docusaurus(self) -> bool:
        """
        Detect if there's already a Docusaurus setup in the target directory
        
        Returns:
            True if existing Docusaurus project is found
        """
        # Check configuration first
        if self.config.generation.force_create_new:
            logger.info(f"🔄 force_create_new=True, creating new documentation structure")
            return False
            
        if not self.config.generation.extend_existing_docs:
            logger.info(f"🚫 extend_existing_docs=False, creating new documentation structure")
            return False
        
        # Check for key Docusaurus files
        key_files = [
            self.output_dir / "docusaurus.config.js",
            self.output_dir / "package.json",
            self.output_dir / "sidebars.js"
        ]
        
        existing_files = [f for f in key_files if f.exists()]
        
        if existing_files:
            logger.info(f"🔍 Detected existing Docusaurus setup at {self.output_dir}")
            logger.info(f"📁 Found {len(existing_files)} existing files: {[f.name for f in existing_files]}")
            return True
        
        logger.info(f"🆕 No existing Docusaurus setup found, will create new one")
        return False
    
    def _create_directory_structure(self) -> None:
        """Create the Docusaurus directory structure"""
        if self.is_existing_docusaurus:
            # Only create our easy_sdk section directories
            directories = [
                self.output_dir / "docs" / self.easy_sdk_section,
                self.output_dir / "docs" / self.easy_sdk_section / "api",
            ]
            logger.info(f"📁 Creating easy-sdk directories in existing Docusaurus setup")
        else:
            # Create full Docusaurus structure
            directories = [
                self.output_dir,
                self.output_dir / "docs",
                self.output_dir / "docs" / "api",
                self.output_dir / "src",
                self.output_dir / "src" / "components",
                self.output_dir / "src" / "pages",
                self.output_dir / "static",
                self.output_dir / "static" / "img",
            ]
            logger.info(f"📁 Creating new Docusaurus project structure")
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _generate_config_files(self) -> List[Path]:
        """Generate Docusaurus configuration files"""
        generated_files = []
        
        if self.is_existing_docusaurus:
            logger.info(f"⚙️ Extending existing Docusaurus configuration")
            # Extend existing sidebar configuration
            self._extend_sidebar_config()
            # Note: We don't modify the main docusaurus.config.js in existing setups
        else:
            logger.info(f"⚙️ Creating new Docusaurus configuration files")
            # docusaurus.config.js
            docusaurus_config = self._create_docusaurus_config()
            config_file = self.output_dir / "docusaurus.config.js"
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(docusaurus_config)
            generated_files.append(config_file)
            
            # sidebar.js
            sidebar_config = self._create_sidebar_config()
            sidebar_file = self.output_dir / "sidebars.js"
            with open(sidebar_file, 'w', encoding='utf-8') as f:
                f.write(sidebar_config)
            generated_files.append(sidebar_file)
        
        return generated_files
    
    def _generate_setup_files(self) -> List[Path]:
        """Generate package.json and other setup files"""
        generated_files = []
        
        if self.is_existing_docusaurus:
            logger.info(f"📦 Skipping setup files (existing Docusaurus project)")
            # Only generate our section README
            readme_content = self._create_easy_sdk_readme()
            readme_file = self.output_dir / "docs" / self.easy_sdk_section / "README.md"
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            generated_files.append(readme_file)
        else:
            logger.info(f"📦 Creating setup files for new Docusaurus project")
            # package.json
            package_json = self._create_package_json()
            package_file = self.output_dir / "package.json"
            with open(package_file, 'w', encoding='utf-8') as f:
                json.dump(package_json, f, indent=2)
            generated_files.append(package_file)
            
            # README.md
            readme_content = self._create_readme()
            readme_file = self.output_dir / "README.md"
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            generated_files.append(readme_file)
        
        return generated_files
    
    def _generate_content(self, analysis_result: Dict[str, Any]) -> List[Path]:
        """Generate documentation content from analysis results"""
        generated_files = []
        
        # Generate main intro page
        intro_file = self._generate_intro_page(analysis_result)
        generated_files.append(intro_file)
        
        # Generate app documentation
        for app_name, app_data in analysis_result.items():
            if isinstance(app_data, dict) and (app_data.get('serializers') or app_data.get('views')):
                app_files = self._generate_app_documentation(app_name, app_data)
                generated_files.extend(app_files)
        
        return generated_files
    
    def _generate_intro_page(self, analysis_result: Dict[str, Any]) -> Path:
        """Generate the main introduction page"""
        apps_with_content = [
            app_name for app_name, app_data in analysis_result.items()
            if isinstance(app_data, dict) and (app_data.get('serializers') or app_data.get('views'))
        ]
        
        # Adjust API paths based on whether we're extending existing setup
        api_link_prefix = "api/" if not self.is_existing_docusaurus else "api/"
        
        # Generate app links
        app_links = ''.join([f"- [{app.title()}](./{api_link_prefix}{app}) - {app} API documentation" + "\n" for app in apps_with_content])
        
        content = f"""---
sidebar_position: 1
---

# {self.config.project_name} API Documentation

{self.config.description}

**Version:** {self.config.version}

## Overview

This documentation provides comprehensive information about the {self.config.project_name} API endpoints, serializers, and data models.

## Available Apps

{app_links}

## Getting Started

### Authentication

Most API endpoints require authentication. Include your API token in the Authorization header:

```http
Authorization: Bearer YOUR_API_TOKEN
```

### Response Format

All API responses follow a consistent JSON format:

```json
{{
  "data": {{}},
  "message": "Success message",
  "success": true
}}
```

### Error Handling

Error responses include detailed information:

```json
{{
  "error": {{
    "detail": "Error description",
    "code": "ERROR_CODE"
  }},
  "success": false
}}
```

## SDKs and Libraries

### JavaScript/TypeScript

```bash
npm install axios
```

```javascript
import axios from 'axios';

const api = axios.create({{
  baseURL: 'http://localhost:8000/api',
  headers: {{
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  }}
}});
```

### Python

```bash
pip install requests
```

```python
import requests

BASE_URL = 'http://localhost:8000/api'
headers = {{
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
}}
```

:::note Generated Documentation

This documentation was automatically generated from Django code analysis using [easy-sdk](https://github.com/your-org/easy-sdk).

:::
"""
        
        # Place intro in correct directory based on setup type
        base_path = self.easy_sdk_section if self.is_existing_docusaurus else ""
        intro_file = self.output_dir / "docs" / base_path / "intro.md"
        intro_file.parent.mkdir(parents=True, exist_ok=True)
        with open(intro_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return intro_file
    
    def _generate_app_documentation(self, app_name: str, app_data: Dict[str, Any]) -> List[Path]:
        """Generate documentation for a specific Django app"""
        generated_files = []
        
        # Create app directory
        base_path = self.easy_sdk_section if self.is_existing_docusaurus else ""
        app_dir = self.output_dir / "docs" / base_path / "api" / app_name
        app_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate app overview
        app_overview = self._generate_app_overview(app_name, app_data)
        generated_files.append(app_overview)
        
        # Generate serializer documentation
        if app_data.get('serializers'):
            serializer_doc = self._generate_serializer_docs(app_name, app_data['serializers'])
            generated_files.append(serializer_doc)
        
        # Generate endpoint documentation
        if app_data.get('views'):
            endpoint_doc = self._generate_endpoint_docs(app_name, app_data['views'])
            generated_files.append(endpoint_doc)
        
        return generated_files
    
    def _generate_app_overview(self, app_name: str, app_data: Dict[str, Any]) -> Path:
        """Generate app overview page"""
        serializer_count = len(app_data.get('serializers', []))
        view_count = len(app_data.get('views', []))
        
        content = f"""---
sidebar_position: 1
---

# {app_name.title()} App

Overview of the {app_name} Django app and its API components.

## Summary

- **Serializers:** {serializer_count}
- **Views:** {view_count}

## Quick Navigation

- [📋 Serializers](./serializers) - Data serialization and validation
- [🔗 Endpoints](./endpoints) - API endpoints and usage examples

## Architecture

The {app_name} app provides the following functionality:

```mermaid
graph TD
    A[Client Request] --> B[Django View]
    B --> C[Serializer Validation]
    C --> D[Model Operations]
    D --> E[Serializer Response]
    E --> F[JSON Response]
```

## Data Models

The app works with the following data structures:

{self._generate_model_overview(app_data)}

## Authentication & Permissions

Most endpoints in this app require authentication. Make sure to include your API token:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \\
     -H "Content-Type: application/json" \\
     http://localhost:8000/api/{app_name}/
```
"""
        
        base_path = self.easy_sdk_section if self.is_existing_docusaurus else ""
        overview_file = self.output_dir / "docs" / base_path / "api" / app_name / "index.md"
        with open(overview_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return overview_file
    
    def _generate_serializer_docs(self, app_name: str, serializers: List[Dict[str, Any]]) -> Path:
        """Generate serializer documentation"""
        content = f"""---
sidebar_position: 2
---

# {app_name.title()} Serializers

Data serialization and validation classes for the {app_name} app.

"""
        
        for serializer in serializers:
            serializer_name = serializer.get('name', 'Unknown')
            fields = serializer.get('fields', {})
            
            content += f"""
## {serializer_name}

{serializer.get('docstring', f'{serializer_name} for handling {app_name} data.')}

**File:** `{serializer.get('file_path', '')}`

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
"""
            
            for field_name, field_info in fields.items():
                field_type = field_info.get('type', 'unknown')
                required = "✅" if field_info.get('required', True) else "❌"
                description = field_info.get('help_text', field_name.replace('_', ' ').title())
                content += f"| `{field_name}` | `{field_type}` | {required} | {description} |\n"
            
            content += f"""
### Usage Examples

#### Creating {serializer_name.replace('Serializer', '')}

```python
from {app_name}.serializers import {serializer_name}

# Validate and create instance
data = {{
{self._generate_example_data(fields)}
}}

serializer = {serializer_name}(data=data)
if serializer.is_valid():
    instance = serializer.save()
    print(f"Created: {{instance}}")
else:
    print(f"Validation errors: {{serializer.errors}}")
```

#### JavaScript/TypeScript Interface

```typescript
interface {serializer_name.replace('Serializer', '')} {{
{self._generate_typescript_interface(fields)}
}}

// Usage example
const {serializer_name.replace('Serializer', '').lower()}: {serializer_name.replace('Serializer', '')} = {{
{self._generate_js_example_data(fields)}
}};
```

#### API Request Example

```bash
curl -X POST "http://localhost:8000/api/{app_name}/{serializer_name.replace('Serializer', '').lower()}/" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -d '{{
{self._generate_json_example_data(fields)}
  }}'
```

---

"""
        
        base_path = self.easy_sdk_section if self.is_existing_docusaurus else ""
        serializer_file = self.output_dir / "docs" / base_path / "api" / app_name / "serializers.md"
        with open(serializer_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return serializer_file
    
    def _generate_endpoint_docs(self, app_name: str, views: List[Dict[str, Any]]) -> Path:
        """Generate endpoint documentation"""
        content = f"""---
sidebar_position: 3
---

# {app_name.title()} API Endpoints

API endpoints and usage examples for the {app_name} app.

"""
        
        for view in views:
            view_name = view.get('name', 'Unknown')
            endpoints = view.get('endpoints', [])
            
            content += f"""
## {view_name}

{view.get('docstring', f'{view_name} API endpoints.')}

**File:** `{view.get('file_path', '')}`

"""
            
            for endpoint in endpoints:
                method = endpoint.get('method', 'GET')
                path = endpoint.get('path', '/')
                
                # Method badge color
                method_color = {
                    'GET': '🟢',
                    'POST': '🔵', 
                    'PUT': '🟡',
                    'PATCH': '🟠',
                    'DELETE': '🔴'
                }.get(method, '⚪')
                
                content += f"""
### {method_color} `{method} {path}`

{endpoint.get('description', f'{method} endpoint for {view_name}.')}

#### Request

```http
{method} {path} HTTP/1.1
Host: localhost:8000
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN
"""
                
                if method in ['POST', 'PUT', 'PATCH']:
                    content += f"""
{{
  "example": "request_data"
}}
"""
                
                content += """
```

#### Python Example

```python
import requests

url = f"http://localhost:8000{path}"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_TOKEN"
}
"""
                
                if method == 'GET':
                    content += f"""
response = requests.get(url, headers=headers)
"""
                elif method == 'POST':
                    content += f"""
data = {{"example": "data"}}
response = requests.post(url, json=data, headers=headers)
"""
                elif method in ['PUT', 'PATCH']:
                    content += f"""
data = {{"example": "data"}}
response = requests.{method.lower()}(url, json=data, headers=headers)
"""
                elif method == 'DELETE':
                    content += f"""
response = requests.delete(url, headers=headers)
"""
                
                content += """
if response.status_code == 200:
    result = response.json()
    print(result)
```

#### JavaScript/Fetch Example

```javascript
const response = await fetch('http://localhost:8000""" + path + """', {
  method: '""" + method + """',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_TOKEN'
  }"""
                
                if method in ['POST', 'PUT', 'PATCH']:
                    content += """,
  body: JSON.stringify({
    example: 'data'
  })"""
                
                content += """
});

const data = await response.json();
console.log(data);
```

#### cURL Example

```bash"""
                
                content += f"""
curl -X {method} "http://localhost:8000{path}" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_TOKEN\""""
                
                if method in ['POST', 'PUT', 'PATCH']:
                    content += """ \\
  -d '{"example": "data"}'"""
                
                content += """
```

---

"""
        
        base_path = self.easy_sdk_section if self.is_existing_docusaurus else ""
        endpoint_file = self.output_dir / "docs" / base_path / "api" / app_name / "endpoints.md"
        with open(endpoint_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return endpoint_file
    
    def _create_docusaurus_config(self) -> str:
        """Create docusaurus.config.js content"""
        return f"""// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

/** @type {{import('@docusaurus/types').Config}} */
const config = {{
  title: '{self.config.project_name}',
  tagline: '{self.config.description}',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://your-docusaurus-test-site.com',
  // Set the /<baseUrl>/ pathname under which your site is served
  baseUrl: '/',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {{
    defaultLocale: 'en',
    locales: ['en'],
  }},

  presets: [
    [
      'classic',
      /** @type {{import('@docusaurus/preset-classic').Options}} */
      ({{
        docs: {{
          sidebarPath: require.resolve('./sidebars.js'),
        }},
        blog: false,
        theme: {{
          customCss: require.resolve('./src/css/custom.css'),
        }},
      }}),
    ],
  ],

  themeConfig:
    /** @type {{import('@docusaurus/preset-classic').ThemeConfig}} */
    ({{
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      navbar: {{
        title: '{self.config.project_name}',
        logo: {{
          alt: 'API Logo',
          src: 'img/logo.svg',
        }},
        items: [
          {{
            type: 'docSidebar',
            sidebarId: 'apiSidebar',
            position: 'left',
            label: 'API Docs',
          }},
          {{
            href: 'https://github.com/your-org/your-repo',
            label: 'GitHub',
            position: 'right',
          }},
        ],
      }},
      footer: {{
        style: 'dark',
        links: [
          {{
            title: 'Documentation',
            items: [
              {{
                label: 'API Reference',
                to: '/docs/intro',
              }},
            ],
          }},
          {{
            title: 'Community',
            items: [
              {{
                label: 'GitHub Issues',
                href: 'https://github.com/your-org/your-repo/issues',
              }},
            ],
          }},
        ],
        copyright: `Copyright © ${{new Date().getFullYear()}} {self.config.project_name}. Built with Docusaurus.`,
      }},
      prism: {{
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['python', 'bash', 'json', 'typescript'],
      }},
    }}),
}};

module.exports = config;
"""
    
    def _create_sidebar_config(self) -> str:
        """Create sidebars.js content"""
        return """/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  apiSidebar: [
    'intro',
    {
      type: 'category',
      label: 'API Reference',
      items: [
        {
          type: 'autogenerated',
          dirName: 'api',
        },
      ],
    },
  ],
};

module.exports = sidebars;
"""
    
    def _create_package_json(self) -> Dict[str, Any]:
        """Create package.json content"""
        return {
            "name": f"{self.config.project_name.lower().replace(' ', '-')}-docs",
            "version": self.config.version,
            "private": True,
            "scripts": {
                "docusaurus": "docusaurus",
                "start": "docusaurus start",
                "build": "docusaurus build",
                "swizzle": "docusaurus swizzle",
                "deploy": "docusaurus deploy",
                "clear": "docusaurus clear",
                "serve": "docusaurus serve",
                "write-translations": "docusaurus write-translations",
                "write-heading-ids": "docusaurus write-heading-ids"
            },
            "dependencies": {
                "@docusaurus/core": "3.8.1",
                "@docusaurus/preset-classic": "3.8.1",
                "@mdx-js/react": "^3.0.0",
                "clsx": "^2.0.0",
                "prism-react-renderer": "^2.3.0",
                "react": "^18.0.0",
                "react-dom": "^18.0.0"
            },
            "devDependencies": {
                "@docusaurus/module-type-aliases": "3.8.1",
                "@docusaurus/tsconfig": "3.8.1",
                "@docusaurus/types": "3.8.1"
            },
            "browserslist": {
                "production": [
                    ">0.5%",
                    "not dead",
                    "not op_mini all"
                ],
                "development": [
                    "last 3 chrome version",
                    "last 3 firefox version",
                    "last 5 safari version"
                ]
            },
            "engines": {
                "node": ">=18.0"
            }
        }
    
    def _create_readme(self) -> str:
        """Create README.md content"""
        return f"""# {self.config.project_name} Documentation

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.

## Installation

```bash
npm install
```

## Local Development

```bash
npm start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

```bash
npm run build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Deployment

Using SSH:

```bash
USE_SSH=true npm run deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> npm run deploy
```

If you are using GitHub Pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.

## Generated Documentation

This documentation was automatically generated from Django code analysis using [easy-sdk](https://github.com/your-org/easy-sdk).

To regenerate:

```bash
easy-sdk /path/to/django/project --format=docusaurus
```
"""
    
    def _generate_model_overview(self, app_data: Dict[str, Any]) -> str:
        """Generate model overview section with multi-language type viewer"""
        serializers = app_data.get('serializers', [])
        if not serializers:
            return "No data models documented."
        
        app_name = app_data.get('app_name', 'unknown')
        
        # Use our dynamic multi-language component
        overview = f"""import DynamicTypeLoader from '@site/src/components/DynamicTypeLoader';

<DynamicTypeLoader 
  appName="{app_name}"
  title="Data Model Definitions"
  showAllVariants={{false}}
/>

### Model Summary

"""
        
        # Add basic summary
        for serializer in serializers:
            name = serializer.get('name', '').replace('Serializer', '')
            fields = serializer.get('fields', {})
            if name and fields:
                overview += f"- **{name}**: {len(fields)} fields\n"
        
        overview += f"""
### 🎯 Why Multiple Languages & Naming Conventions?

Different development environments have different conventions:

- **Frontend Teams**: Often prefer `camelCase` properties for JavaScript/TypeScript
- **Backend Teams**: May prefer `snake_case` to match Python/Django conventions  
- **Mobile Teams**: iOS uses `PascalCase`, Android varies by language
- **Integration Teams**: Need to match existing codebases and style guides

Easy-SDK generates **all variants automatically** so every team can use their preferred style without manual conversion.

"""
        
        return overview
    
    def _generate_example_data(self, fields: Dict[str, Any]) -> str:
        """Generate example data for Python code"""
        examples = []
        for field_name, field_info in fields.items():
            if field_info.get('required', True):
                field_type = field_info.get('type', 'string')
                if field_type in ['integer', 'number']:
                    examples.append(f'    "{field_name}": 123')
                elif field_type == 'boolean':
                    examples.append(f'    "{field_name}": true')
                else:
                    examples.append(f'    "{field_name}": "example_value"')
        comma_newline = ',\\n'
        return comma_newline.join(examples[:5])  # Limit to 5 fields
    
    def _generate_typescript_interface(self, fields: Dict[str, Any]) -> str:
        """Generate TypeScript interface fields"""
        examples = []
        for field_name, field_info in fields.items():
            field_type = field_info.get('type', 'string')
            ts_type = {
                'integer': 'number',
                'float': 'number', 
                'boolean': 'boolean',
                'date': 'string',
                'datetime': 'string'
            }.get(field_type, 'string')
            
            optional = '' if field_info.get('required', True) else '?'
            examples.append(f'  {field_name}{optional}: {ts_type};')
        newline = '\\n'
        return newline.join(examples)
    
    def _generate_js_example_data(self, fields: Dict[str, Any]) -> str:
        """Generate JavaScript example data"""
        examples = []
        for field_name, field_info in fields.items():
            if field_info.get('required', True):
                field_type = field_info.get('type', 'string')
                if field_type in ['integer', 'number']:
                    examples.append(f'  {field_name}: 123')
                elif field_type == 'boolean':
                    examples.append(f'  {field_name}: true')
                else:
                    examples.append(f'  {field_name}: "example_value"')
        comma_newline = ',\\n'
        return comma_newline.join(examples[:5])
    
    def _generate_json_example_data(self, fields: Dict[str, Any]) -> str:
        """Generate JSON example data"""
        examples = []
        for field_name, field_info in fields.items():
            if field_info.get('required', True):
                field_type = field_info.get('type', 'string')
                if field_type in ['integer', 'number']:
                    examples.append(f'    "{field_name}": 123')
                elif field_type == 'boolean':
                    examples.append(f'    "{field_name}": true')
                else:
                    examples.append(f'    "{field_name}": "example_value"')
        comma_newline = ',\\n'
        return comma_newline.join(examples[:5])
    
    def _extend_sidebar_config(self) -> None:
        """Extend existing sidebar configuration with easy-sdk section"""
        sidebar_file = self.output_dir / "sidebars.js"
        
        if not sidebar_file.exists():
            logger.warning("No existing sidebars.js found to extend")
            return
            
        try:
            # Read existing sidebar config
            with open(sidebar_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if easy-sdk section already exists
            if self.easy_sdk_section in content:
                logger.info(f"♻️ easy-sdk section already exists in sidebar, skipping extension")
                return
            
            # Find where to inject our section - look for the main sidebar array
            easy_sdk_section = f"""    {{
      type: 'category',
      label: '🤖 Easy SDK Generated',
      collapsed: false,
      items: [
        '{self.easy_sdk_section}/intro',
        {{
          type: 'category', 
          label: 'API Reference',
          items: [
            {{
              type: 'autogenerated',
              dirName: '{self.easy_sdk_section}/api',
            }},
          ],
        }},
      ],
    }},"""
            
            # Try to find the main sidebar array and add our section
            import re
            
            # Pattern to find sidebar arrays
            sidebar_pattern = r'(const\s+\w+\s*=\s*\{[^}]*\[)(.*?)(\][^}]*\})'
            match = re.search(sidebar_pattern, content, re.DOTALL)
            
            if match:
                before = match.group(1)
                existing_items = match.group(2)
                after = match.group(3)
                
                # Add our section at the beginning
                newline = "\\n"
                updated_content = before + newline + easy_sdk_section + newline + existing_items + after
                
                with open(sidebar_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                    
                logger.info(f"✅ Extended existing sidebar configuration with easy-sdk section")
            else:
                logger.warning("Could not parse existing sidebar.js structure")
                
        except Exception as e:
            logger.error(f"Failed to extend sidebar config: {e}")
    
    def _create_easy_sdk_readme(self) -> str:
        """Create README for easy-sdk section in existing Docusaurus"""
        return f"""# 🤖 Easy SDK Generated Documentation

This section contains automatically generated API documentation for **{self.config.project_name}**.

## What's Inside

This documentation includes:

- 📚 **API Endpoints** - Complete reference for all REST API endpoints
- 🔧 **Data Models** - Multi-language serializer schemas with configurable naming conventions
- 🚀 **Code Examples** - Ready-to-use code snippets in 8 programming languages
- 🔐 **Authentication** - Security and authorization details
- 🎯 **Type Definitions** - Generated types in TypeScript, Python, Java, C#, Go, Rust, Swift, and Kotlin

## Generated Content

- **Project:** {self.config.project_name}
- **Version:** {self.config.version} 
- **Generated:** {self._get_current_timestamp()}

## 🌐 Multi-Language Type Generation

import MultiLanguageTypeViewer from '@site/src/components/MultiLanguageTypeViewer';

<MultiLanguageTypeViewer 
  appName="products"
  title="🚀 Complete Multi-Language API Types"
/>

Easy-SDK automatically generates API type definitions in **8 programming languages** with **36 naming convention variants**. Choose the language and style that matches your project's needs!

### 📁 Generated Directory Structure

```
easy_sdk/
└── types_multi/
    ├── typescript/
    │   ├── PascalCase_camelCase/    # Standard TypeScript style
    │   ├── PascalCase_snake_case/   # Mixed style
    │   ├── snake_case_snake_case/   # Python style
    │   └── ... (33 more variants)
    ├── python/
    │   ├── PascalCase_snake_case/   # Standard Python style
    │   └── ... (35 more variants)
    ├── java/
    │   ├── PascalCase_camelCase/    # Standard Java style
    │   └── ... (35 more variants)
    └── ... (5 more languages)
```

## Navigation

- [Introduction](./intro) - Getting started guide
- [API Reference](./api/) - Complete API documentation

:::info Auto-Generated
This documentation is automatically generated by [easy-sdk](https://github.com/your-org/easy-sdk). 
To update, re-run the easy-sdk generator on your Django project.
:::

## Regenerating Documentation

To update this documentation with the latest changes:

```bash
easy-sdk /path/to/django/project --format docusaurus
```

The generator will detect this existing Docusaurus setup and only update the easy-sdk sections.
"""
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for documentation"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")