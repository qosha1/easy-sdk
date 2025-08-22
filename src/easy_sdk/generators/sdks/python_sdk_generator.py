"""
Python SDK Generator - Generates a complete Python client library
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .base_sdk_generator import BaseSDKGenerator

logger = logging.getLogger(__name__)


class PythonSDKGenerator(BaseSDKGenerator):
    """
    Generate a complete Python SDK with modern async/await support,
    type hints, proper error handling, and intelligent structure.
    """
    
    def __init__(self, config, library_name: str = None):
        super().__init__(config, "python")
        self.library_name = library_name or "api_client"
        self.package_name = self._to_snake_case(self.library_name)
        
    def generate_sdk(self, analysis_result: Dict[str, Any]) -> List[Path]:
        """Generate complete Python SDK from Django analysis"""
        logger.info(f"🐍 Generating Python SDK: {self.library_name}")
        
        # Extract and analyze API structure
        api_structure = self._extract_api_structure(analysis_result)
        
        # Create project structure
        self._generate_project_structure()
        
        generated_files = []
        
        # Generate core client files
        generated_files.extend(self._generate_core_files(api_structure))
        
        # Generate models for each app
        for app in api_structure['apps']:
            model_files = self._generate_models(app['name'], app['serializers'])
            generated_files.extend(model_files)
        
        # Generate client classes for each app
        for app in api_structure['apps']:
            client_file = self._generate_client_class(app['name'], app['endpoints'])
            generated_files.append(client_file)
        
        # Generate main SDK client
        main_client_file = self._generate_main_client(api_structure)
        generated_files.append(main_client_file)
        
        logger.info(f"✅ Python SDK generated with {len(generated_files)} files")
        return generated_files
    
    def _generate_project_structure(self) -> None:
        """Create the Python package structure"""
        self._create_directory_structure()
        
        # Create package directory
        package_dir = self.output_dir / self.package_name
        package_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (package_dir / "models").mkdir(exist_ok=True)
        (package_dir / "clients").mkdir(exist_ok=True)
        (package_dir / "utils").mkdir(exist_ok=True)
        
        logger.info(f"📁 Created Python package structure: {package_dir}")
    
    def _generate_core_files(self, api_structure: Dict[str, Any]) -> List[Path]:
        """Generate core SDK files"""
        generated_files = []
        
        # Generate setup.py
        setup_content = self._generate_setup_py(api_structure)
        setup_file = self._write_file(self.output_dir / "setup.py", setup_content)
        generated_files.append(setup_file)
        
        # Generate requirements.txt
        requirements_content = self._generate_requirements()
        requirements_file = self._write_file(self.output_dir / "requirements.txt", requirements_content)
        generated_files.append(requirements_file)
        
        # Generate package __init__.py
        init_content = self._generate_package_init()
        init_file = self._write_file(
            self.output_dir / self.package_name / "__init__.py", 
            init_content
        )
        generated_files.append(init_file)
        
        # Generate base client
        base_client_content = self._generate_base_client(api_structure)
        base_client_file = self._write_file(
            self.output_dir / self.package_name / "base_client.py",
            base_client_content
        )
        generated_files.append(base_client_file)
        
        # Generate exceptions
        exceptions_content = self._generate_exceptions()
        exceptions_file = self._write_file(
            self.output_dir / self.package_name / "exceptions.py",
            exceptions_content
        )
        generated_files.append(exceptions_file)
        
        # Generate utilities
        utils_content = self._generate_utils()
        utils_file = self._write_file(
            self.output_dir / self.package_name / "utils" / "__init__.py",
            utils_content
        )
        generated_files.append(utils_file)
        
        return generated_files
    
    def _generate_models(self, app_name: str, serializers: List[Dict]) -> List[Tuple[Path, str]]:
        """Generate data models from serializers"""
        generated_files = []
        
        # Create models directory for this app
        models_dir = self.output_dir / self.package_name / "models"
        
        # Generate __init__.py for models
        models_init_content = self._generate_models_init(serializers)
        models_init_file = self._write_file(models_dir / "__init__.py", models_init_content)
        generated_files.append(models_init_file)
        
        # Generate individual model files
        for serializer in serializers:
            model_content = self._generate_model_class(serializer)
            model_name = serializer['name'].replace('Serializer', '').lower()
            model_file = self._write_file(
                models_dir / f"{model_name}.py",
                model_content
            )
            generated_files.append(model_file)
        
        return generated_files
    
    def _generate_client_class(self, app_name: str, endpoints: List[Dict]) -> Path:
        """Generate the main client class for an app"""
        class_name = f"{self._to_class_name(app_name)}Client"
        
        # Group endpoints by operation
        operations = self._group_endpoints_into_operations(endpoints)
        
        content = f'''"""
{app_name.title()} API client
Auto-generated by easy-sdk
"""

from typing import Dict, List, Optional, Any
import asyncio
from ..base_client import BaseAPIClient
from ..exceptions import APIError


class {class_name}(BaseAPIClient):
    """
    Client for {app_name} API operations
    
    Provides methods for all {app_name} endpoints with proper
    type hints, error handling, and async support.
    """
    
    def __init__(self, base_client: BaseAPIClient):
        """Initialize {app_name} client with shared base client"""
        self.base_client = base_client
        self.base_url = base_client.base_url
        self.session = base_client.session
    
{self._generate_client_methods(operations)}
'''
        
        client_file = self._write_file(
            self.output_dir / self.package_name / "clients" / f"{app_name}_client.py",
            content
        )
        
        return client_file
    
    def _generate_main_client(self, api_structure: Dict[str, Any]) -> Path:
        """Generate the main SDK client that combines all app clients"""
        content = f'''"""
Main {self.library_name} SDK Client
Auto-generated by easy-sdk
"""

from typing import Optional
from .base_client import BaseAPIClient
{self._generate_client_imports(api_structure)}


class {self._to_class_name(self.library_name)}Client:
    """
    Main SDK client that provides access to all API endpoints
    
    Usage:
        client = {self._to_class_name(self.library_name)}Client(api_key="your-key")
        result = await client.users.list_users()
    """
    
    def __init__(
        self,
        base_url: str = "{api_structure.get('base_url_pattern', '/api')}",
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize the main SDK client
        
        Args:
            base_url: API base URL
            api_key: Authentication API key
            timeout: Request timeout in seconds
        """
        self.base_client = BaseAPIClient(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout
        )
        
        # Initialize app clients
{self._generate_client_properties(api_structure)}
    
    async def close(self):
        """Close the HTTP session"""
        await self.base_client.close()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
'''
        
        main_file = self._write_file(
            self.output_dir / self.package_name / "client.py",
            content
        )
        
        return main_file
    
    def _generate_setup_py(self, api_structure: Dict[str, Any]) -> str:
        """Generate setup.py for the Python package"""
        return f'''"""
Setup configuration for {self.library_name}
Auto-generated by easy-sdk
"""

from setuptools import setup, find_packages

setup(
    name="{self.package_name}",
    version="1.0.0",
    description="Python SDK for API integration",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
'''
    
    def _generate_requirements(self) -> str:
        """Generate requirements.txt"""
        return '''aiohttp>=3.8.0
pydantic>=2.0.0
typing-extensions>=4.0.0
'''
    
    def _generate_package_init(self) -> str:
        """Generate package __init__.py"""
        return f'''"""
{self.library_name} Python SDK
Auto-generated by easy-sdk
"""

from .client import {self._to_class_name(self.library_name)}Client
from .exceptions import APIError, ValidationError, AuthenticationError, NotFoundError

__version__ = "1.0.0"
__all__ = [
    "{self._to_class_name(self.library_name)}Client",
    "APIError",
    "ValidationError", 
    "AuthenticationError",
    "NotFoundError"
]
'''
    
    def _generate_base_client(self, api_structure: Dict[str, Any]) -> str:
        """Generate base HTTP client"""
        auth_strategy = api_structure.get('auth_strategy', 'token')
        
        return f'''"""
Base API client with HTTP handling, authentication, and error management
Auto-generated by easy-sdk
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import aiohttp
from .exceptions import APIError, ValidationError, AuthenticationError, NotFoundError

logger = logging.getLogger(__name__)


class BaseAPIClient:
    """
    Base HTTP client with authentication, retries, and error handling
    
    Handles:
    - {auth_strategy.upper()} authentication
    - Request/response logging
    - Automatic retries with backoff
    - Standard error response parsing
    """
    
    def __init__(
        self, 
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize base client
        
        Args:
            base_url: API base URL
            api_key: Authentication key
            timeout: Request timeout in seconds  
            max_retries: Maximum number of retries
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        
        # Create session with proper headers
        self.session = None
        self._session_created = False
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if not self.session or self.session.closed:
            headers = {{"Content-Type": "application/json"}}
            
            # Add authentication header based on strategy
            if self.api_key:
{self._generate_auth_header_logic(auth_strategy)}
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=self.timeout
            )
            self._session_created = True
    
    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retries and error handling
        
        Args:
            method: HTTP method
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            **kwargs: Additional aiohttp parameters
            
        Returns:
            Response data
            
        Raises:
            APIError: For API errors
            ValidationError: For validation errors
            AuthenticationError: For auth errors
            NotFoundError: For 404 errors
        """
        await self._ensure_session()
        
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        
        # Prepare request data
        json_data = json.dumps(data) if data else None
        
        # Retry logic
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"{{method}} {{url}} (attempt {{attempt + 1}})")
                
                async with self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=json_data,
                    **kwargs
                ) as response:
                    # Handle different response types
                    if response.content_type == 'application/json':
                        response_data = await response.json()
                    else:
                        response_data = {{"text": await response.text()}}
                    
                    # Check for errors
                    if response.status >= 400:
                        self._handle_error_response(response.status, response_data)
                    
                    logger.debug(f"{{method}} {{url}} -> {{response.status}}")
                    return response_data
                    
            except aiohttp.ClientError as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Request failed, retrying in {{wait_time}}s: {{e}}")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Request failed after {{self.max_retries}} retries: {{e}}")
                    raise APIError(f"Request failed: {{e}}")
        
        # This shouldn't be reached, but just in case
        raise APIError(f"Request failed after retries: {{last_exception}}")
    
    def _handle_error_response(self, status_code: int, response_data: Dict[str, Any]):
        """Handle error responses and raise appropriate exceptions"""
        error_message = self._extract_error_message(response_data)
        
        if status_code == 400:
            raise ValidationError(error_message, status_code, response_data)
        elif status_code == 401:
            raise AuthenticationError(error_message, status_code, response_data) 
        elif status_code == 404:
            raise NotFoundError(error_message, status_code, response_data)
        else:
            raise APIError(error_message, status_code, response_data)
    
    def _extract_error_message(self, response_data: Dict[str, Any]) -> str:
        """Extract error message from response"""
        # Try common error message fields
        for field in ['message', 'error', 'detail', 'non_field_errors']:
            if field in response_data:
                error = response_data[field]
                if isinstance(error, list) and error:
                    return str(error[0])
                return str(error)
        
        return f"API Error: {{response_data}}"
    
    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    # Convenience methods
    async def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """GET request"""
        return await self.request('GET', endpoint, params=params, **kwargs)
    
    async def post(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """POST request"""
        return await self.request('POST', endpoint, data=data, **kwargs)
    
    async def put(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """PUT request"""
        return await self.request('PUT', endpoint, data=data, **kwargs)
    
    async def patch(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """PATCH request"""
        return await self.request('PATCH', endpoint, data=data, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """DELETE request"""
        return await self.request('DELETE', endpoint, **kwargs)
'''
    
    def _generate_auth_header_logic(self, auth_strategy: str) -> str:
        """Generate authentication header logic based on strategy"""
        if auth_strategy == 'token':
            return '''                headers["Authorization"] = f"Token {self.api_key}"'''
        elif auth_strategy == 'bearer':
            return '''                headers["Authorization"] = f"Bearer {self.api_key}"'''
        elif auth_strategy == 'jwt':
            return '''                headers["Authorization"] = f"Bearer {self.api_key}"'''
        else:
            return '''                headers["Authorization"] = f"Token {self.api_key}"'''
    
    def _generate_exceptions(self) -> str:
        """Generate exception classes"""
        return '''"""
API exception classes
Auto-generated by easy-sdk
"""

from typing import Any, Dict, Optional


class APIError(Exception):
    """Base API error"""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}


class ValidationError(APIError):
    """API validation error (400)"""
    pass


class AuthenticationError(APIError):
    """API authentication error (401)"""
    pass


class NotFoundError(APIError):
    """API not found error (404)"""
    pass
'''
    
    def _generate_utils(self) -> str:
        """Generate utility functions"""
        return '''"""
Utility functions for the SDK
Auto-generated by easy-sdk
"""

from typing import Any, Dict, List


def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case to camelCase"""
    components = snake_str.split('_')
    return components[0] + ''.join(word.capitalize() for word in components[1:])


def camel_to_snake(camel_str: str) -> str:
    """Convert camelCase to snake_case"""
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\\1_\\2', camel_str)
    return re.sub('([a-z0-9])([A-Z])', r'\\1_\\2', s1).lower()


def clean_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values from dictionary"""
    return {k: v for k, v in data.items() if v is not None}
'''
    
    def _generate_models_init(self, serializers: List[Dict]) -> str:
        """Generate models __init__.py"""
        imports = []
        for serializer in serializers:
            model_name = serializer['name'].replace('Serializer', '')
            file_name = model_name.lower()
            imports.append(f"from .{file_name} import {model_name}")
        
        all_exports = [serializer['name'].replace('Serializer', '') for serializer in serializers]
        
        return f'''"""
Data models
Auto-generated by easy-sdk
"""

{chr(10).join(imports)}

__all__ = {all_exports}
'''
    
    def _generate_model_class(self, serializer: Dict) -> str:
        """Generate a Pydantic model class from serializer"""
        model_name = serializer['name'].replace('Serializer', '')
        fields = serializer.get('fields', {})
        
        # Generate field definitions
        field_definitions = []
        imports = set(['from typing import Optional', 'from pydantic import BaseModel, Field'])
        
        for field_name, field_info in fields.items():
            python_type = self._get_python_type(field_info, imports)
            field_def = self._generate_field_definition(field_name, field_info, python_type)
            field_definitions.append(field_def)
        
        import_lines = '\n'.join(sorted(imports))
        fields_code = '\n    '.join(field_definitions)
        
        return f'''"""
{model_name} data model
Auto-generated by easy-sdk
"""

{import_lines}


class {model_name}(BaseModel):
    """
    {serializer.get('docstring', f'{model_name} data model')}
    """
    
    {fields_code}
    
    class Config:
        """Pydantic model configuration"""
        extra = "forbid"  # Forbid extra fields
        validate_assignment = True  # Validate on assignment
'''
    
    def _get_python_type(self, field_info: Dict, imports: set) -> str:
        """Get Python type annotation for a field"""
        field_type = field_info.get('type', 'string')
        required = field_info.get('required', True)
        allow_null = field_info.get('allow_null', False)
        
        # Map Django types to Python types
        type_mapping = {
            'CharField': 'str',
            'TextField': 'str',
            'EmailField': 'str',
            'URLField': 'str',
            'SlugField': 'str',
            'UUIDField': 'str',
            'IntegerField': 'int',
            'BigIntegerField': 'int',
            'SmallIntegerField': 'int',
            'PositiveIntegerField': 'int',
            'FloatField': 'float',
            'DecimalField': 'float',
            'BooleanField': 'bool',
            'DateField': 'str',
            'DateTimeField': 'str',
            'TimeField': 'str',
            'JSONField': 'dict',
            'DictField': 'dict',
            'ListField': 'list',
        }
        
        python_type = type_mapping.get(field_type, 'str')
        
        # Handle choices
        if field_info.get('choices'):
            choices = [str(choice[0]) if isinstance(choice, (list, tuple)) else str(choice) 
                      for choice in field_info['choices']]
            imports.add('from typing import Literal')
            python_type = f"Literal[{', '.join(repr(c) for c in choices)}]"
        
        # Handle optional fields
        if not required or allow_null:
            python_type = f"Optional[{python_type}]"
        
        return python_type
    
    def _generate_field_definition(self, field_name: str, field_info: Dict, python_type: str) -> str:
        """Generate a field definition for Pydantic model"""
        required = field_info.get('required', True)
        default_value = field_info.get('default')
        help_text = field_info.get('help_text', '')
        
        # Build field definition
        if required and default_value is None:
            field_def = f"{field_name}: {python_type}"
        else:
            if default_value is not None:
                if isinstance(default_value, str):
                    default_str = f'"{default_value}"'
                else:
                    default_str = str(default_value)
                field_def = f"{field_name}: {python_type} = {default_str}"
            else:
                field_def = f"{field_name}: {python_type} = None"
        
        # Add Field() for additional validation or metadata
        field_constraints = []
        
        if field_info.get('max_length'):
            field_constraints.append(f"max_length={field_info['max_length']}")
        
        if help_text:
            field_constraints.append(f'description="{help_text}"')
        
        if field_constraints:
            constraint_str = ', '.join(field_constraints)
            field_def += f" = Field({constraint_str})"
        
        return field_def
    
    def _generate_client_methods(self, operations: List[Dict]) -> str:
        """Generate client methods for operations"""
        methods = []
        
        for operation in operations:
            for endpoint in operation['endpoints']:
                method_name = self._generate_method_name(endpoint)
                method_code = self._generate_method_code(endpoint, operation)
                methods.append(method_code)
        
        return '\n\n'.join(methods)
    
    def _generate_method_name(self, endpoint: Dict) -> str:
        """Generate a Python method name from endpoint"""
        method = endpoint['method'].lower()
        path = endpoint['path']
        
        # Extract resource and action
        path_parts = [p for p in path.split('/') if p and not p.startswith('{')]
        resource = path_parts[-1] if path_parts else 'resource'
        
        # Generate descriptive method names
        if method == 'get':
            if '{' in path:  # Detail endpoint
                return f"get_{resource}"
            else:  # List endpoint
                return f"list_{resource}"
        elif method == 'post':
            return f"create_{resource}"
        elif method == 'put':
            return f"update_{resource}"
        elif method == 'patch':
            return f"partial_update_{resource}"
        elif method == 'delete':
            return f"delete_{resource}"
        
        return f"{method}_{resource}"
    
    def _generate_method_code(self, endpoint: Dict, operation: Dict) -> str:
        """Generate code for a single API method"""
        method_name = self._generate_method_name(endpoint)
        http_method = endpoint['method'].upper()
        path = endpoint['path']
        description = endpoint.get('description', f'{http_method} {path}')
        
        # Extract path parameters
        import re
        path_params = re.findall(r'\{(\w+)\}', path)
        
        # Generate method signature
        params = []
        if path_params:
            params.extend([f"{param}: Union[str, int]" for param in path_params])
        
        # Add data parameter for POST/PUT/PATCH
        if http_method in ['POST', 'PUT', 'PATCH']:
            params.append("data: Optional[Dict[str, Any]] = None")
        
        # Add query parameters
        params.append("params: Optional[Dict[str, Any]] = None")
        
        param_str = ', '.join(params)
        if param_str:
            param_str = ', ' + param_str
        
        # Generate method body
        path_substitution = path
        for param in path_params:
            path_substitution = path_substitution.replace(f'{{{param}}}', f'{{{{param}}}}')
        
        if http_method in ['POST', 'PUT', 'PATCH']:
            request_call = f'await self.base_client.{http_method.lower()}(endpoint, data=data, params=params)'
        else:
            request_call = f'await self.base_client.{http_method.lower()}(endpoint, params=params)'
        
        return f'''    async def {method_name}(self{param_str}) -> Dict[str, Any]:
        """
        {description}
        
        Args:
{self._generate_method_args_doc(path_params, http_method)}
            
        Returns:
            API response data
            
        Raises:
            APIError: If the request fails
        """
        endpoint = f"{path_substitution}"
        return {request_call}'''
    
    def _generate_method_args_doc(self, path_params: List[str], http_method: str) -> str:
        """Generate method arguments documentation"""
        docs = []
        
        for param in path_params:
            docs.append(f"            {param}: {param.title()} identifier")
        
        if http_method in ['POST', 'PUT', 'PATCH']:
            docs.append("            data: Request payload data")
        
        docs.append("            params: Query parameters")
        
        return '\n'.join(docs)
    
    def _generate_client_imports(self, api_structure: Dict[str, Any]) -> str:
        """Generate imports for app clients"""
        imports = []
        for app in api_structure['apps']:
            class_name = f"{self._to_class_name(app['name'])}Client"
            imports.append(f"from .clients.{app['name']}_client import {class_name}")
        
        return '\n'.join(imports)
    
    def _generate_client_properties(self, api_structure: Dict[str, Any]) -> str:
        """Generate client properties for each app"""
        properties = []
        for app in api_structure['apps']:
            app_name = app['name']
            class_name = f"{self._to_class_name(app_name)}Client"
            property_name = self._to_snake_case(app_name)
            
            properties.append(f"        self.{property_name} = {class_name}(self.base_client)")
        
        return '\n'.join(properties)