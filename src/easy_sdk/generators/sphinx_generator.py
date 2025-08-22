"""
Sphinx documentation generator for Django API documentation
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, Template

from ..core.config import DjangoDocsConfig

logger = logging.getLogger(__name__)


class SphinxDocumentationGenerator:
    """
    Generates Sphinx-compatible reStructuredText documentation
    from Django analysis results. Can either create new documentation
    or extend existing Sphinx setups.
    """
    
    def __init__(self, config: DjangoDocsConfig):
        self.config = config
        self.output_dir = config.output.sphinx_output_dir
        self.is_existing_sphinx = self._detect_existing_sphinx()
        self.easy_sdk_section = "easy_sdk"
        
        # Initialize Jinja2 environment for templates
        template_dir = Path(__file__).parent.parent / "templates" / "sphinx"
        if template_dir.exists():
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(template_dir)),
                trim_blocks=True,
                lstrip_blocks=True
            )
        else:
            # Create basic templates in memory
            self.jinja_env = Environment()
            self._create_builtin_templates()
    
    def generate_documentation(self, analysis_result: Optional[Dict[str, Any]] = None) -> List[Path]:
        """
        Generate complete Sphinx documentation
        
        Args:
            analysis_result: Analysis results from Django components
        
        Returns:
            List of generated file paths
        """
        generated_files = []
        
        try:
            # Create output directory structure
            self._create_directory_structure()
            
            if self.is_existing_sphinx:
                logger.info(f"⚙️ Extending existing Sphinx configuration")
                # Generate our section index
                easy_sdk_index = self._generate_easy_sdk_index(analysis_result)
                generated_files.append(easy_sdk_index)
                
                # Extend existing main index
                self._extend_main_index()
            else:
                logger.info(f"⚙️ Creating new Sphinx project")
                # Generate main index file
                index_file = self._generate_index(analysis_result)
                generated_files.append(index_file)
                
                # Generate configuration file
                conf_file = self._generate_conf_py()
                generated_files.append(conf_file)
                
                # Generate static assets
                static_files = self._generate_static_assets()
                generated_files.extend(static_files)
            
            # Generate app documentation from analysis results
            if analysis_result:
                app_files = self._generate_app_documentation(analysis_result)
                generated_files.extend(app_files)
            
            logger.info(f"Generated {len(generated_files)} Sphinx documentation files")
            
        except Exception as e:
            logger.error(f"Failed to generate Sphinx documentation: {str(e)}")
        
        return generated_files
    
    def _detect_existing_sphinx(self) -> bool:
        """
        Detect if there's already a Sphinx setup in the target directory
        
        Returns:
            True if existing Sphinx project is found
        """
        # Check configuration first
        if self.config.generation.force_create_new:
            logger.info(f"🔄 force_create_new=True, creating new documentation structure")
            return False
            
        if not self.config.generation.extend_existing_docs:
            logger.info(f"🚫 extend_existing_docs=False, creating new documentation structure")
            return False
        
        # Check for key Sphinx files
        key_files = [
            self.output_dir / "conf.py",
            self.output_dir / "index.rst",
            self.output_dir / "Makefile"
        ]
        
        existing_files = [f for f in key_files if f.exists()]
        
        if existing_files:
            logger.info(f"🔍 Detected existing Sphinx setup at {self.output_dir}")
            logger.info(f"📁 Found {len(existing_files)} existing files: {[f.name for f in existing_files]}")
            return True
        
        logger.info(f"🆕 No existing Sphinx setup found, will create new one")
        return False
    
    def generate_app_documentation(self, app_name: str, app_analysis: Dict[str, Any]) -> List[Path]:
        """
        Generate documentation for a specific Django app
        
        Args:
            app_name: Name of the Django app
            app_analysis: Analysis results for the app
            
        Returns:
            List of generated file paths
        """
        generated_files = []
        
        try:
            # Use correct directory structure based on setup type
            base_path = self.easy_sdk_section if self.is_existing_sphinx else ""
            app_dir = self.output_dir / base_path / "apps" / app_name
            app_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate app index
            app_index = self._generate_app_index(app_name, app_analysis)
            generated_files.append(app_index)
            
            # Generate serializer documentation
            if 'serializers' in app_analysis:
                serializer_doc = self._generate_serializer_documentation(
                    app_name, app_analysis['serializers']
                )
                generated_files.append(serializer_doc)
            
            # Generate view/endpoint documentation
            if 'views' in app_analysis:
                endpoint_doc = self._generate_endpoint_documentation(
                    app_name, app_analysis['views']
                )
                generated_files.append(endpoint_doc)
            
            # Generate model documentation if available
            if 'models' in app_analysis:
                model_doc = self._generate_model_documentation(
                    app_name, app_analysis['models']
                )
                generated_files.append(model_doc)
            
        except Exception as e:
            logger.error(f"Failed to generate documentation for app {app_name}: {str(e)}")
        
        return generated_files
    
    def _create_directory_structure(self) -> None:
        """Create the Sphinx directory structure"""
        directories = [
            self.output_dir,
            self.output_dir / "apps",
            self.output_dir / "_static",
            self.output_dir / "_templates",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _generate_index(self, analysis_result: Optional[Dict[str, Any]] = None) -> Path:
        """Generate main index.rst file"""
        template = self.jinja_env.get_template("index.rst")
        
        # Get list of apps with documentation
        apps = []
        if analysis_result:
            apps = [app_name for app_name, app_data in analysis_result.items() 
                   if isinstance(app_data, dict) and (
                       app_data.get('serializers') or app_data.get('views')
                   )]
        
        content = template.render(
            project_name=self.config.project_name,
            version=self.config.version,
            description=self.config.description,
            apps=apps,
        )
        
        index_file = self.output_dir / "index.rst"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return index_file
    
    def _generate_conf_py(self) -> Path:
        """Generate Sphinx configuration file"""
        template = self.jinja_env.get_template("conf.py")
        
        content = template.render(
            project_name=self.config.project_name,
            version=self.config.version,
            author=self.config.author,
            sphinx_theme_options=self.config.generation.sphinx_theme_options,
        )
        
        conf_file = self.output_dir / "conf.py"
        with open(conf_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return conf_file
    
    def _generate_app_documentation(self, analysis_result: Dict[str, Any]) -> List[Path]:
        """Generate documentation for all analyzed apps"""
        generated_files = []
        
        # First, create the main apps index file
        apps_with_content = []
        for app_name, app_data in analysis_result.items():
            if isinstance(app_data, dict) and (app_data.get('serializers') or app_data.get('views')):
                apps_with_content.append(app_name)
        
        if apps_with_content:
            apps_index_file = self._generate_apps_index(apps_with_content)
            generated_files.append(apps_index_file)
            
            # Generate individual app documentation
            for app_name in apps_with_content:
                app_analysis = analysis_result[app_name]
                app_files = self.generate_app_documentation(app_name, app_analysis)
                generated_files.extend(app_files)
        
        return generated_files
    
    def _generate_apps_index(self, apps: List[str]) -> Path:
        """Generate main apps index file"""
        apps_dir = self.output_dir / "apps"
        apps_dir.mkdir(parents=True, exist_ok=True)
        
        lines = [
            "Django Apps",
            "===========",
            "",
            "Documentation for Django apps discovered in the project.",
            "",
            ".. toctree::",
            "   :maxdepth: 2",
            "   :caption: Apps:",
            "",
        ]
        
        for app_name in apps:
            lines.append(f"   {app_name}/index")
        
        content = "\n".join(lines)
        apps_index_file = apps_dir / "index.rst"
        with open(apps_index_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return apps_index_file
    
    def _generate_app_index(self, app_name: str, app_analysis: Dict[str, Any]) -> Path:
        """Generate index file for a specific app"""
        template = self.jinja_env.get_template("app_index.rst")
        
        content = template.render(
            app_name=app_name,
            app_analysis=app_analysis,
        )
        
        app_index_file = self.output_dir / "apps" / app_name / "index.rst"
        with open(app_index_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return app_index_file
    
    def _generate_serializer_documentation(self, app_name: str, serializers: List[Dict[str, Any]]) -> Path:
        """Generate documentation for app serializers"""
        template = self.jinja_env.get_template("serializers.rst")
        
        content = template.render(
            app_name=app_name,
            serializers=serializers,
        )
        
        serializer_file = self.output_dir / "apps" / app_name / "serializers.rst"
        with open(serializer_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return serializer_file
    
    def _generate_endpoint_documentation(self, app_name: str, views: List[Dict[str, Any]]) -> Path:
        """Generate documentation for app endpoints"""
        template = self.jinja_env.get_template("endpoints.rst")
        
        # Extract all endpoints from views
        all_endpoints = []
        for view in views:
            endpoints = view.get('endpoints', [])
            for endpoint in endpoints:
                endpoint['view_name'] = view.get('name', '')
                all_endpoints.append(endpoint)
        
        content = template.render(
            app_name=app_name,
            endpoints=all_endpoints,
            views=views,
        )
        
        endpoint_file = self.output_dir / "apps" / app_name / "endpoints.rst"
        with open(endpoint_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return endpoint_file
    
    def _generate_model_documentation(self, app_name: str, models: List[Dict[str, Any]]) -> Path:
        """Generate documentation for app models"""
        template = self.jinja_env.get_template("models.rst")
        
        content = template.render(
            app_name=app_name,
            models=models,
        )
        
        model_file = self.output_dir / "apps" / app_name / "models.rst"
        with open(model_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return model_file
    
    def _generate_static_assets(self) -> List[Path]:
        """Generate static assets for documentation"""
        static_files = []
        
        try:
            # Create custom CSS
            css_content = self._generate_custom_css()
            css_file = self.output_dir / "_static" / "custom.css"
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write(css_content)
            static_files.append(css_file)
            
            # Create JavaScript enhancements
            js_content = self._generate_custom_js()
            js_file = self.output_dir / "_static" / "custom.js"
            with open(js_file, 'w', encoding='utf-8') as f:
                f.write(js_content)
            static_files.append(js_file)
            
        except Exception as e:
            logger.warning(f"Failed to generate static assets: {str(e)}")
        
        return static_files
    
    def _generate_custom_css(self) -> str:
        """Generate custom CSS for documentation"""
        return """
/* Custom styles for Django API Documentation */

.api-endpoint {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 0.25rem;
    padding: 1rem;
    margin: 1rem 0;
}

.api-method {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-weight: bold;
    text-transform: uppercase;
    font-size: 0.75rem;
    margin-right: 0.5rem;
}

.api-method.get {
    background-color: #28a745;
    color: white;
}

.api-method.post {
    background-color: #007bff;
    color: white;
}

.api-method.put {
    background-color: #ffc107;
    color: black;
}

.api-method.patch {
    background-color: #fd7e14;
    color: white;
}

.api-method.delete {
    background-color: #dc3545;
    color: white;
}

.api-path {
    font-family: 'Courier New', monospace;
    background-color: #e9ecef;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
}

.field-type {
    color: #6c757d;
    font-style: italic;
}

.required-field {
    color: #dc3545;
    font-weight: bold;
}

.optional-field {
    color: #28a745;
}

.code-example {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 0.25rem;
    padding: 1rem;
    font-family: 'Courier New', monospace;
    white-space: pre-wrap;
}
"""
    
    def _generate_custom_js(self) -> str:
        """Generate custom JavaScript for documentation"""
        return """
// Custom JavaScript for Django API Documentation

document.addEventListener('DOMContentLoaded', function() {
    // Add copy to clipboard functionality for code examples
    const codeExamples = document.querySelectorAll('.code-example');
    
    codeExamples.forEach(function(codeBlock) {
        const copyButton = document.createElement('button');
        copyButton.textContent = 'Copy';
        copyButton.className = 'copy-button';
        copyButton.style.cssText = 'position: absolute; top: 0.5rem; right: 0.5rem; padding: 0.25rem 0.5rem; background: #007bff; color: white; border: none; border-radius: 0.25rem; cursor: pointer;';
        
        codeBlock.style.position = 'relative';
        codeBlock.appendChild(copyButton);
        
        copyButton.addEventListener('click', function() {
            navigator.clipboard.writeText(codeBlock.textContent.replace('Copy', '').trim());
            copyButton.textContent = 'Copied!';
            setTimeout(function() {
                copyButton.textContent = 'Copy';
            }, 2000);
        });
    });
    
    // Add collapsible sections for detailed field information
    const fieldSections = document.querySelectorAll('.field-details');
    
    fieldSections.forEach(function(section) {
        const header = section.querySelector('h4, h5, h6');
        if (header) {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                const content = section.querySelector('.field-content');
                if (content) {
                    content.style.display = content.style.display === 'none' ? 'block' : 'none';
                }
            });
        }
    });
});
"""
    
    def _create_builtin_templates(self) -> None:
        """Create builtin Jinja2 templates"""
        # Main index template
        index_template = Template("""{{ project_name }}
{{ "=" * project_name|length }}

{{ description }}

Version: {{ version }}

{% if apps %}
.. toctree::
   :maxdepth: 2
   :caption: Contents:

   apps/index
{% endif %}

API Reference
=============

This documentation provides comprehensive information about the {{ project_name }} API endpoints, serializers, and data models.
{% if apps %}

The following Django apps have been documented:
{% for app in apps %}
- :doc:`apps/{{ app }}/index` - {{ app|title }} app documentation
{% endfor %}
{% else %}

.. note::
   No Django apps with serializers or views were found for documentation.
{% endif %}

.. note::
   This documentation was automatically generated from Django code analysis.
""")
        self.jinja_env.globals['index_template'] = index_template
        
        # Configuration template
        conf_template = Template("""# Configuration file for the Sphinx documentation builder.

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.abspath('../../'))

# -- Project information -----------------------------------------------------
project = '{{ project_name }}'
copyright = '2024, {{ author }}'
author = '{{ author }}'
version = '{{ version }}'
release = '{{ version }}'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
html_theme = 'alabaster'
html_static_path = ['_static']

html_theme_options = {{ sphinx_theme_options|tojson|replace('false', 'False')|replace('true', 'True')|replace('null', 'None') }}

html_css_files = [
    'custom.css',
]

html_js_files = [
    'custom.js',
]

# -- Extension configuration -------------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'django': ('https://docs.djangoproject.com/en/stable/', 'https://docs.djangoproject.com/en/stable/_objects/'),
    'drf': ('https://www.django-rest-framework.org/', None),
}
""")
        self.jinja_env.globals['conf_template'] = conf_template
        
        # App index template
        app_index_template = Template("""{{ app_name|title }} App
{{ "=" * (app_name|length + 4) }}

Overview of the {{ app_name }} Django app and its API components.

.. toctree::
   :maxdepth: 2

   serializers
   endpoints
   {% if app_analysis.models %}models{% endif %}

Summary
-------

{% if app_analysis.serializers %}
Serializers: {{ app_analysis.serializers|length }}
{% endif %}
{% if app_analysis.views %}
Views: {{ app_analysis.views|length }}
{% endif %}
{% if app_analysis.models %}
Models: {{ app_analysis.models|length }}
{% endif %}
""")
        self.jinja_env.globals['app_index_template'] = app_index_template
        
        # Serializers template
        serializers_template = Template("""{{ app_name|title }} Serializers
{{ "=" * (app_name|length + 12) }}

{% for serializer in serializers %}
{{ serializer.name }}
{{ "-" * serializer.name|length }}

{{ serializer.docstring or "Serializer for " + serializer.name.replace("Serializer", "") + " data." }}

**File:** ``{{ serializer.file_path }}``

{% if serializer.base_classes %}
**Inherits from:** {{ serializer.base_classes|join(", ") }}
{% endif %}

Fields
^^^^^^

{% for field_name, field in serializer.fields.items() %}
.. py:attribute:: {{ field_name }}
   :type: {{ field.type }}
   
   {% if field.ai_description %}{{ field.ai_description }}{% else %}{{ field.help_text or field_name.replace("_", " ").title() }}{% endif %}
   
   {% if field.required %}**Required**{% else %}**Optional**{% endif %}
   {% if field.default is not none %} (Default: ``{{ field.default }}``){% endif %}
   
   {% if field.choices %}
   **Choices:** {{ field.choices|join(", ") }}
   {% endif %}
   
   {% if field.max_length %}
   **Max Length:** {{ field.max_length }}
   {% endif %}

{% endfor %}

{% if serializer.ai_insights and serializer.ai_insights.examples %}
Example Usage
^^^^^^^^^^^^^

Request Example:

.. code-block:: json
   :caption: POST Request Body

   {{ serializer.ai_insights.examples.request_example or '{}' }}

Response Example:

.. code-block:: json
   :caption: 200 OK Response

   {{ serializer.ai_insights.examples.response_example or '{}' }}

{% else %}
Example Usage
^^^^^^^^^^^^^

Python Usage:

.. code-block:: python
   :caption: Creating {{ serializer.name.replace("Serializer", "") }} instance

   from {{ app_name }}.serializers import {{ serializer.name }}
   
   # Create serializer instance
   serializer = {{ serializer.name }}(data=request.data)
   if serializer.is_valid():
       instance = serializer.save()
   else:
       print(serializer.errors)

JavaScript/TypeScript Usage:

.. code-block:: javascript
   :caption: Frontend API Call

   // Fetch {{ serializer.name.replace("Serializer", "").lower() }} data
   const response = await fetch('/api/{{ app_name }}/{{ serializer.name.replace("Serializer", "").lower() }}/', {
     method: 'GET',
     headers: {
       'Content-Type': 'application/json',
       'Authorization': `Bearer ${token}`
     }
   });
   const data = await response.json();

cURL Example:

.. code-block:: bash
   :caption: Command Line API Call

   curl -X GET "http://localhost:8000/api/{{ app_name }}/{{ serializer.name.replace("Serializer", "").lower() }}/" \
     -H "Accept: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN"

{% endif %}

{% endfor %}
""")
        self.jinja_env.globals['serializers_template'] = serializers_template
        
        # Endpoints template  
        endpoints_template = Template("""{{ app_name|title }} API Endpoints
{{ "=" * (app_name|length + 14) }}

{% for endpoint in endpoints %}
{% set method_class = endpoint.method|lower %}
.. raw:: html

   <div class="api-endpoint">
       <span class="api-method {{ method_class }}">{{ endpoint.method }}</span>
       <span class="api-path">{{ endpoint.path }}</span>
   </div>

{{ endpoint.ai_description or endpoint.description or "API endpoint for " + endpoint.view_class }}

**View Class:** ``{{ endpoint.view_class }}``

{% if endpoint.function_name %}
**Function:** ``{{ endpoint.function_name }}``
{% endif %}

{% if endpoint.serializer_class %}
**Serializer:** ``{{ endpoint.serializer_class }}``
{% endif %}

{% if endpoint.permission_classes %}
**Permissions:** {{ endpoint.permission_classes|join(", ") }}
{% endif %}

{% if endpoint.ai_parameters %}
Parameters
^^^^^^^^^^

{% for param in endpoint.ai_parameters %}
- **{{ param.name }}** ({{ param.type }}): {{ param.description }}
{% endfor %}
{% endif %}

{% if endpoint.ai_responses %}
Responses
^^^^^^^^^

{% for status, response in endpoint.ai_responses.items() %}
**{{ status }}**

.. code-block:: json

   {{ response.example or '{}' }}

{% endfor %}
{% endif %}

Examples
^^^^^^^^

HTTP Request:

.. code-block:: http
   :caption: {{ endpoint.method }} {{ endpoint.path }}

   {{ endpoint.method }} {{ endpoint.path }} HTTP/1.1
   Host: localhost:8000
   Content-Type: application/json
   Authorization: Bearer YOUR_TOKEN
   
   {% if endpoint.method in ['POST', 'PUT', 'PATCH'] %}{{ endpoint.ai_examples.request or '{}' }}{% endif %}

Python Requests:

.. code-block:: python
   :caption: Using Python requests library

   import requests
   
   url = "http://localhost:8000{{ endpoint.path }}"
   headers = {
       "Content-Type": "application/json",
       "Authorization": "Bearer YOUR_TOKEN"
   }
   
   {% if endpoint.method == 'GET' %}response = requests.get(url, headers=headers)
   {% elif endpoint.method == 'POST' %}data = {{ endpoint.ai_examples.request or '{}' }}
   response = requests.post(url, json=data, headers=headers)
   {% elif endpoint.method == 'PUT' %}data = {{ endpoint.ai_examples.request or '{}' }}
   response = requests.put(url, json=data, headers=headers)
   {% elif endpoint.method == 'PATCH' %}data = {{ endpoint.ai_examples.request or '{}' }}
   response = requests.patch(url, json=data, headers=headers)
   {% elif endpoint.method == 'DELETE' %}response = requests.delete(url, headers=headers)
   {% endif %}
   
   if response.status_code == 200:
       result = response.json()
       print(result)

JavaScript/Fetch:

.. code-block:: javascript
   :caption: Using Fetch API

   const url = 'http://localhost:8000{{ endpoint.path }}';
   const options = {
     method: '{{ endpoint.method }}',
     headers: {
       'Content-Type': 'application/json',
       'Authorization': 'Bearer YOUR_TOKEN'
     }{% if endpoint.method in ['POST', 'PUT', 'PATCH'] %},
     body: JSON.stringify({{ endpoint.ai_examples.request or '{}' }}){% endif %}
   };
   
   fetch(url, options)
     .then(response => response.json())
     .then(data => console.log(data))
     .catch(error => console.error('Error:', error));

cURL Command:

.. code-block:: bash
   :caption: Command line with cURL

   curl -X {{ endpoint.method }} "http://localhost:8000{{ endpoint.path }}" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN"{% if endpoint.method in ['POST', 'PUT', 'PATCH'] %} \
     -d '{{ endpoint.ai_examples.request or '{}' }}'{% endif %}

---

{% endfor %}
""")
        self.jinja_env.globals['endpoints_template'] = endpoints_template
        
        # Models template
        models_template = Template("""{{ app_name|title }} Models
{{ "=" * (app_name|length + 7) }}

{% for model in models %}
{{ model.name }}
{{ "-" * model.name|length }}

{{ model.docstring or "Django model representing " + model.name + " data." }}

**File:** ``{{ model.file_path }}``

{% if model.fields %}
Fields
^^^^^^

{% for field in model.fields %}
.. py:attribute:: {{ field.name }}
   :type: {{ field.type }}
   
   {{ field.help_text or field.name.replace("_", " ").title() }}

{% endfor %}
{% endif %}

{% endfor %}
""")
        self.jinja_env.globals['models_template'] = models_template
        
        # Register templates
        def get_template(name):
            template_map = {
                'index.rst': index_template,
                'conf.py': conf_template, 
                'app_index.rst': app_index_template,
                'serializers.rst': serializers_template,
                'endpoints.rst': endpoints_template,
                'models.rst': models_template,
            }
            return template_map.get(name, Template(""))
            
        self.jinja_env.get_template = get_template
    
    def _extend_main_index(self) -> None:
        """Extend existing index.rst with easy-sdk section"""
        index_file = self.output_dir / "index.rst"
        
        if not index_file.exists():
            logger.warning("No existing index.rst found to extend")
            return
            
        try:
            # Read existing index
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if easy-sdk section already exists
            if self.easy_sdk_section in content:
                logger.info(f"♻️ easy-sdk section already exists in index.rst, skipping extension")
                return
            
            # Add our section to the toctree
            easy_sdk_entry = f"""   {self.easy_sdk_section}/index"""
            
            # Find toctree and add our section
            import re
            toctree_pattern = r'(\.\.[\s]+toctree::[^\n]*\n(?:[\s]+:[^\n]*\n)*)(.*?)(\n\n|\nIndices|\Z)'
            match = re.search(toctree_pattern, content, re.DOTALL)
            
            if match:
                toctree_header = match.group(1)
                existing_entries = match.group(2)
                after_toctree = match.group(3)
                
                # Add our entry at the beginning of toctree
                updated_content = content.replace(
                    toctree_header + existing_entries + after_toctree,
                    toctree_header + "\\n" + easy_sdk_entry + "\\n" + existing_entries + after_toctree
                )
                
                with open(index_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                    
                logger.info(f"✅ Extended existing index.rst with easy-sdk section")
            else:
                logger.warning("Could not find toctree in existing index.rst")
                
        except Exception as e:
            logger.error(f"Failed to extend main index: {e}")
    
    def _generate_easy_sdk_index(self, analysis_result: Optional[Dict[str, Any]] = None) -> Path:
        """Generate index file for easy-sdk section in existing Sphinx"""
        apps = []
        if analysis_result:
            apps = [app_name for app_name, app_data in analysis_result.items() 
                   if isinstance(app_data, dict) and (
                       app_data.get('serializers') or app_data.get('views')
                   )]
        
        content = f"""🤖 Easy SDK Generated Documentation
=====================================

This section contains automatically generated API documentation for **{self.config.project_name}**.

.. note::
   This documentation is automatically generated by `easy-sdk <https://github.com/your-org/easy-sdk>`_.
   To update, re-run the easy-sdk generator on your Django project.

Project Information
-------------------

- **Project:** {self.config.project_name}
- **Version:** {self.config.version}
- **Description:** {self.config.description}
- **Generated:** {self._get_current_timestamp()}

API Reference
-------------

.. toctree::
   :maxdepth: 2
   :caption: Django Apps:

"""
        
        for app in apps:
            content += f"   apps/{app}/index\\n"
        
        content += f"""

Getting Started
---------------

Authentication
^^^^^^^^^^^^^^

Most API endpoints require authentication. Include your API token in the Authorization header:

.. code-block:: http

   Authorization: Bearer YOUR_API_TOKEN

Response Format
^^^^^^^^^^^^^^^

All API responses follow a consistent JSON format:

.. code-block:: json

   {{
     "data": {{}},
     "message": "Success message", 
     "success": true
   }}

Error Handling
^^^^^^^^^^^^^^

Error responses include detailed information:

.. code-block:: json

   {{
     "error": {{
       "detail": "Error description",
       "code": "ERROR_CODE"
     }},
     "success": false
   }}

SDKs and Libraries
------------------

JavaScript/TypeScript
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   npm install axios

.. code-block:: javascript

   import axios from 'axios';
   
   const api = axios.create({{
     baseURL: 'http://localhost:8000/api',
     headers: {{
       'Authorization': 'Bearer YOUR_TOKEN',
       'Content-Type': 'application/json'
     }}
   }});

Python
^^^^^^

.. code-block:: bash

   pip install requests

.. code-block:: python

   import requests
   
   BASE_URL = 'http://localhost:8000/api'
   headers = {{
       'Authorization': 'Bearer YOUR_TOKEN',
       'Content-Type': 'application/json'
   }}

Regenerating Documentation
--------------------------

To update this documentation with the latest changes:

.. code-block:: bash

   easy-sdk /path/to/django/project --format sphinx

The generator will detect this existing Sphinx setup and only update the easy-sdk sections.
"""
        
        easy_sdk_index = self.output_dir / self.easy_sdk_section / "index.rst"
        easy_sdk_index.parent.mkdir(parents=True, exist_ok=True)
        with open(easy_sdk_index, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return easy_sdk_index
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for documentation"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")