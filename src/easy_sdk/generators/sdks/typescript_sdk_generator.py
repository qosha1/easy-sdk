"""
TypeScript/JavaScript SDK Generator - Generates a complete TypeScript/JavaScript client library
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .base_sdk_generator import BaseSDKGenerator

logger = logging.getLogger(__name__)


class TypeScriptSDKGenerator(BaseSDKGenerator):
    """
    Generate a complete TypeScript SDK with modern async/await support,
    proper type definitions, error handling, and modular structure.
    Supports both Node.js and browser environments.
    """
    
    def __init__(self, config, library_name: str = None, include_nodejs: bool = True):
        super().__init__(config, "typescript")
        self.library_name = library_name or "api-client"
        self.package_name = self._to_kebab_case(self.library_name)
        self.include_nodejs = include_nodejs
        
    def generate_sdk(self, analysis_result: Dict[str, Any]) -> List[Path]:
        """Generate complete TypeScript SDK from Django analysis"""
        logger.info(f"🔵 Generating TypeScript SDK: {self.library_name}")
        
        # Extract and analyze API structure
        api_structure = self._extract_api_structure(analysis_result)
        
        # Create project structure
        self._generate_project_structure()
        
        generated_files = []
        
        # Generate core files
        generated_files.extend(self._generate_core_files(api_structure))
        
        # Generate type definitions
        generated_files.extend(self._generate_types(api_structure))
        
        # Generate client classes for each app
        for app in api_structure['apps']:
            client_file = self._generate_client_class(app['name'], app['endpoints'])
            generated_files.append(client_file)
        
        # Generate main SDK client
        main_client_file = self._generate_main_client(api_structure)
        generated_files.append(main_client_file)
        
        logger.info(f"✅ TypeScript SDK generated with {len(generated_files)} files")
        return generated_files
    
    def _generate_project_structure(self) -> None:
        """Create the TypeScript/JavaScript package structure"""
        self._create_directory_structure()
        
        # Create src directory structure
        src_dir = self.output_dir / "src"
        src_dir.mkdir(exist_ok=True)
        
        (src_dir / "types").mkdir(exist_ok=True)
        (src_dir / "clients").mkdir(exist_ok=True)
        (src_dir / "utils").mkdir(exist_ok=True)
        
        logger.info(f"📁 Created TypeScript package structure: {src_dir}")
    
    def _generate_core_files(self, api_structure: Dict[str, Any]) -> List[Path]:
        """Generate core SDK files"""
        generated_files = []
        
        # Generate package.json
        package_content = self._generate_package_json(api_structure)
        package_file = self._write_file(self.output_dir / "package.json", package_content)
        generated_files.append(package_file)
        
        # Generate tsconfig.json
        tsconfig_content = self._generate_tsconfig()
        tsconfig_file = self._write_file(self.output_dir / "tsconfig.json", tsconfig_content)
        generated_files.append(tsconfig_file)
        
        # Generate base client
        base_client_content = self._generate_base_client(api_structure)
        base_client_file = self._write_file(
            self.output_dir / "src" / "BaseClient.ts",
            base_client_content
        )
        generated_files.append(base_client_file)
        
        # Generate exceptions
        exceptions_content = self._generate_exceptions()
        exceptions_file = self._write_file(
            self.output_dir / "src" / "exceptions.ts",
            exceptions_content
        )
        generated_files.append(exceptions_file)
        
        # Generate utilities
        utils_content = self._generate_utils()
        utils_file = self._write_file(
            self.output_dir / "src" / "utils" / "index.ts",
            utils_content
        )
        generated_files.append(utils_file)
        
        return generated_files
    
    def _generate_types(self, api_structure: Dict[str, Any]) -> List[Path]:
        """Generate TypeScript type definitions"""
        generated_files = []
        
        # Generate types for each app
        for app in api_structure['apps']:
            types_content = self._generate_app_types(app)
            types_file = self._write_file(
                self.output_dir / "src" / "types" / f"{app['name']}.ts",
                types_content
            )
            generated_files.append(types_file)
        
        # Generate common types
        common_types_content = self._generate_common_types(api_structure)
        common_types_file = self._write_file(
            self.output_dir / "src" / "types" / "common.ts",
            common_types_content
        )
        generated_files.append(common_types_file)
        
        # Generate types index
        types_index_content = self._generate_types_index(api_structure)
        types_index_file = self._write_file(
            self.output_dir / "src" / "types" / "index.ts",
            types_index_content
        )
        generated_files.append(types_index_file)
        
        return generated_files
    
    def _generate_models(self, app_name: str, serializers: List[Dict]) -> List[Tuple[Path, str]]:
        """Generate TypeScript interfaces from serializers"""
        # In TypeScript, models are handled as type definitions in _generate_types
        return []
    
    def _generate_client_class(self, app_name: str, endpoints: List[Dict]) -> Path:
        """Generate the main client class for an app"""
        class_name = f"{self._to_pascal_case(app_name)}Client"
        
        # Group endpoints by operation
        operations = self._group_endpoints_into_operations(endpoints)
        
        content = f'''/**
 * {app_name.title()} API client
 * Auto-generated by easy-sdk
 */

import {{ BaseAPIClient }} from '../BaseClient';
import {{ APIError }} from '../exceptions';
import type {{ {self._generate_type_imports(operations)} }} from '../types/{app_name}';
import type {{ APIResponse, QueryParams }} from '../types/common';

export class {class_name} {{
  constructor(private baseClient: BaseAPIClient) {{}}

{self._generate_client_methods(operations)}
}}
'''
        
        client_file = self._write_file(
            self.output_dir / "src" / "clients" / f"{self._to_pascal_case(app_name)}Client.ts",
            content
        )
        
        return client_file
    
    def _generate_main_client(self, api_structure: Dict[str, Any]) -> Path:
        """Generate the main SDK client that combines all app clients"""
        content = f'''/**
 * Main {self.library_name} SDK Client
 * Auto-generated by easy-sdk
 */

import {{ BaseAPIClient }} from './BaseClient';
{self._generate_client_imports(api_structure)}

export interface {self._to_pascal_case(self.library_name)}ClientConfig {{
  baseUrl?: string;
  apiKey?: string;
  timeout?: number;
}}

/**
 * Main SDK client that provides access to all API endpoints
 * 
 * @example
 * ```typescript
 * const client = new {self._to_pascal_case(self.library_name)}Client({{
 *   apiKey: 'your-api-key',
 *   baseUrl: 'https://api.example.com'
 * }});
 * 
 * const users = await client.users.listUsers();
 * ```
 */
export class {self._to_pascal_case(self.library_name)}Client {{
  private baseClient: BaseAPIClient;
  
{self._generate_client_properties(api_structure)}

  constructor(config: {self._to_pascal_case(self.library_name)}ClientConfig = {{}}) {{
    this.baseClient = new BaseAPIClient({{
      baseUrl: config.baseUrl ?? '{api_structure.get('base_url_pattern', '/api')}',
      apiKey: config.apiKey,
      timeout: config.timeout ?? 30000
    }});
    
    // Initialize app clients
{self._generate_client_initialization(api_structure)}
  }}

  /**
   * Close any open connections
   */
  async close(): Promise<void> {{
    await this.baseClient.close();
  }}
}}

// Export everything
export * from './types';
export * from './exceptions';
export {{ BaseAPIClient }} from './BaseClient';
'''
        
        main_file = self._write_file(
            self.output_dir / "src" / "index.ts",
            content
        )
        
        return main_file
    
    def _generate_package_json(self, api_structure: Dict[str, Any]) -> str:
        """Generate package.json for the TypeScript package"""
        return json.dumps({
            "name": self.package_name,
            "version": "1.0.0",
            "description": f"TypeScript SDK for {self.library_name}",
            "main": "dist/index.js",
            "module": "dist/index.mjs",
            "types": "dist/index.d.ts",
            "exports": {
                ".": {
                    "types": "./dist/index.d.ts",
                    "import": "./dist/index.mjs",
                    "require": "./dist/index.js"
                }
            },
            "files": [
                "dist"
            ],
            "scripts": {
                "build": "tsup src/index.ts --format cjs,esm --dts",
                "dev": "tsup src/index.ts --format cjs,esm --dts --watch",
                "type-check": "tsc --noEmit",
                "lint": "eslint src --ext .ts",
                "test": "jest"
            },
            "keywords": ["api", "client", "sdk", "typescript"],
            "author": "easy-sdk",
            "license": "MIT",
            "dependencies": {
                "cross-fetch": "^3.1.5" if self.include_nodejs else "^4.0.0"
            },
            "devDependencies": {
                "@types/node": "^20.0.0",
                "typescript": "^5.0.0",
                "tsup": "^8.0.0",
                "eslint": "^8.0.0",
                "@typescript-eslint/eslint-plugin": "^6.0.0",
                "@typescript-eslint/parser": "^6.0.0",
                "jest": "^29.0.0",
                "@types/jest": "^29.0.0",
                "ts-jest": "^29.0.0"
            },
            "engines": {
                "node": ">=16.0.0"
            }
        }, indent=2)
    
    def _generate_tsconfig(self) -> str:
        """Generate tsconfig.json"""
        return json.dumps({
            "compilerOptions": {
                "target": "ES2020",
                "lib": ["ES2020", "DOM"],
                "module": "ESNext",
                "moduleResolution": "node",
                "esModuleInterop": True,
                "allowSyntheticDefaultImports": True,
                "strict": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "declaration": True,
                "declarationMap": True,
                "sourceMap": True,
                "outDir": "./dist",
                "rootDir": "./src",
                "resolveJsonModule": True
            },
            "include": ["src/**/*"],
            "exclude": ["node_modules", "dist", "**/*.test.ts"]
        }, indent=2)
    
    def _generate_base_client(self, api_structure: Dict[str, Any]) -> str:
        """Generate base HTTP client"""
        auth_strategy = api_structure.get('auth_strategy', 'token')
        
        # Determine fetch import based on environment
        fetch_import = "import 'cross-fetch/polyfill';" if self.include_nodejs else ""
        
        return f'''/**
 * Base API client with HTTP handling, authentication, and error management
 * Auto-generated by easy-sdk
 */

{fetch_import}
import {{ APIError, ValidationError, AuthenticationError, NotFoundError }} from './exceptions';

export interface BaseClientConfig {{
  baseUrl: string;
  apiKey?: string;
  timeout?: number;
  maxRetries?: number;
}}

export interface RequestOptions {{
  method: string;
  endpoint: string;
  params?: Record<string, any>;
  data?: any;
  headers?: Record<string, string>;
}}

/**
 * Base HTTP client with authentication, retries, and error handling
 * 
 * Handles:
 * - {auth_strategy.upper()} authentication
 * - Request/response logging
 * - Automatic retries with exponential backoff
 * - Standard error response parsing
 */
export class BaseAPIClient {{
  private baseUrl: string;
  private apiKey?: string;
  private timeout: number;
  private maxRetries: number;
  private abortController?: AbortController;

  constructor(config: BaseClientConfig) {{
    this.baseUrl = config.baseUrl.replace(/\\/$/, '');
    this.apiKey = config.apiKey;
    this.timeout = config.timeout ?? 30000;
    this.maxRetries = config.maxRetries ?? 3;
  }}

  /**
   * Make HTTP request with retries and error handling
   */
  async request<T = any>(options: RequestOptions): Promise<T> {{
    const {{ method, endpoint, params, data, headers = {{}} }} = options;
    
    // Build URL
    const url = new URL(endpoint, this.baseUrl);
    if (params) {{
      Object.entries(params).forEach(([key, value]) => {{
        if (value !== undefined && value !== null) {{
          url.searchParams.append(key, String(value));
        }}
      }});
    }}

    // Prepare headers
    const requestHeaders: Record<string, string> = {{
      'Content-Type': 'application/json',
      ...headers
    }};

    // Add authentication header
    if (this.apiKey) {{
{self._generate_auth_header_logic_ts(auth_strategy)}
    }}

    // Prepare request options
    this.abortController = new AbortController();
    const fetchOptions: RequestInit = {{
      method: method.toUpperCase(),
      headers: requestHeaders,
      signal: this.abortController.signal
    }};

    if (data && ['POST', 'PUT', 'PATCH'].includes(method.toUpperCase())) {{
      fetchOptions.body = JSON.stringify(data);
    }}

    // Set timeout
    const timeoutId = setTimeout(() => {{
      this.abortController?.abort();
    }}, this.timeout);

    // Retry logic
    let lastError: Error | null = null;
    
    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {{
      try {{
        const response = await fetch(url.toString(), fetchOptions);
        clearTimeout(timeoutId);

        // Parse response
        const contentType = response.headers.get('content-type');
        let responseData: any;
        
        if (contentType && contentType.includes('application/json')) {{
          responseData = await response.json();
        }} else {{
          responseData = {{ text: await response.text() }};
        }}

        // Handle error responses
        if (!response.ok) {{
          this.handleErrorResponse(response.status, responseData);
        }}

        return responseData as T;

      }} catch (error) {{
        lastError = error as Error;
        
        if (attempt < this.maxRetries && !this.abortController?.signal.aborted) {{
          const waitTime = Math.pow(2, attempt) * 1000; // Exponential backoff
          await this.sleep(waitTime);
          
          // Reset abort controller for retry
          this.abortController = new AbortController();
          fetchOptions.signal = this.abortController.signal;
          
          continue;
        }}
      }}
    }}

    clearTimeout(timeoutId);
    throw new APIError(`Request failed after ${{this.maxRetries}} retries: ${{lastError?.message}}`);
  }}

  private handleErrorResponse(status: number, data: any): never {{
    const message = this.extractErrorMessage(data);
    
    switch (status) {{
      case 400:
        throw new ValidationError(message, status, data);
      case 401:
        throw new AuthenticationError(message, status, data);
      case 404:
        throw new NotFoundError(message, status, data);
      default:
        throw new APIError(message, status, data);
    }}
  }}

  private extractErrorMessage(data: any): string {{
    // Try common error message fields
    const errorFields = ['message', 'error', 'detail', 'non_field_errors'];
    
    for (const field of errorFields) {{
      if (data[field]) {{
        const error = data[field];
        if (Array.isArray(error) && error.length > 0) {{
          return String(error[0]);
        }}
        return String(error);
      }}
    }}
    
    return `API Error: ${{JSON.stringify(data)}}`;
  }}

  private sleep(ms: number): Promise<void> {{
    return new Promise(resolve => setTimeout(resolve, ms));
  }}

  /**
   * Close any open connections and cancel pending requests
   */
  async close(): Promise<void> {{
    this.abortController?.abort();
  }}

  // Convenience methods
  async get<T = any>(endpoint: string, params?: Record<string, any>): Promise<T> {{
    return this.request<T>({{ method: 'GET', endpoint, params }});
  }}

  async post<T = any>(endpoint: string, data?: any): Promise<T> {{
    return this.request<T>({{ method: 'POST', endpoint, data }});
  }}

  async put<T = any>(endpoint: string, data?: any): Promise<T> {{
    return this.request<T>({{ method: 'PUT', endpoint, data }});
  }}

  async patch<T = any>(endpoint: string, data?: any): Promise<T> {{
    return this.request<T>({{ method: 'PATCH', endpoint, data }});
  }}

  async delete<T = any>(endpoint: string): Promise<T> {{
    return this.request<T>({{ method: 'DELETE', endpoint }});
  }}
}}
'''
    
    def _generate_auth_header_logic_ts(self, auth_strategy: str) -> str:
        """Generate authentication header logic for TypeScript"""
        if auth_strategy == 'token':
            return '''      requestHeaders['Authorization'] = `Token ${this.apiKey}`;'''
        elif auth_strategy == 'bearer':
            return '''      requestHeaders['Authorization'] = `Bearer ${this.apiKey}`;'''
        elif auth_strategy == 'jwt':
            return '''      requestHeaders['Authorization'] = `Bearer ${this.apiKey}`;'''
        else:
            return '''      requestHeaders['Authorization'] = `Token ${this.apiKey}`;'''
    
    def _generate_exceptions(self) -> str:
        """Generate exception classes"""
        return '''/**
 * API exception classes
 * Auto-generated by easy-sdk
 */

export class APIError extends Error {
  public statusCode?: number;
  public responseData?: any;

  constructor(
    message: string,
    statusCode?: number,
    responseData?: any
  ) {
    super(message);
    this.name = 'APIError';
    this.statusCode = statusCode;
    this.responseData = responseData;
    
    // Maintain proper stack trace for where our error was thrown (only available on V8)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, APIError);
    }
  }
}

export class ValidationError extends APIError {
  constructor(message: string, statusCode?: number, responseData?: any) {
    super(message, statusCode, responseData);
    this.name = 'ValidationError';
  }
}

export class AuthenticationError extends APIError {
  constructor(message: string, statusCode?: number, responseData?: any) {
    super(message, statusCode, responseData);
    this.name = 'AuthenticationError';
  }
}

export class NotFoundError extends APIError {
  constructor(message: string, statusCode?: number, responseData?: any) {
    super(message, statusCode, responseData);
    this.name = 'NotFoundError';
  }
}
'''
    
    def _generate_utils(self) -> str:
        """Generate utility functions"""
        return '''/**
 * Utility functions for the SDK
 * Auto-generated by easy-sdk
 */

/**
 * Convert snake_case to camelCase
 */
export function snakeToCamel(str: string): string {
  return str.replace(/_([a-z])/g, (match, letter) => letter.toUpperCase());
}

/**
 * Convert camelCase to snake_case
 */
export function camelToSnake(str: string): string {
  return str.replace(/([A-Z])/g, '_$1').toLowerCase();
}

/**
 * Remove undefined values from an object
 */
export function cleanObject<T extends Record<string, any>>(obj: T): Partial<T> {
  const cleaned: Partial<T> = {};
  Object.entries(obj).forEach(([key, value]) => {
    if (value !== undefined) {
      cleaned[key as keyof T] = value;
    }
  });
  return cleaned;
}

/**
 * Deep merge two objects
 */
export function deepMerge<T extends Record<string, any>>(target: T, source: Partial<T>): T {
  const result = { ...target };
  
  Object.entries(source).forEach(([key, value]) => {
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      result[key as keyof T] = deepMerge(result[key as keyof T] as any, value);
    } else {
      result[key as keyof T] = value as T[keyof T];
    }
  });
  
  return result;
}
'''
    
    def _generate_app_types(self, app: Dict) -> str:
        """Generate TypeScript interfaces for an app"""
        interfaces = []
        
        # Generate interfaces from serializers
        for serializer in app.get('serializers', []):
            interface_name = serializer['name'].replace('Serializer', '')
            interface_code = self._generate_interface(serializer, interface_name)
            interfaces.append(interface_code)
        
        return f'''/**
 * Type definitions for {app['name']} app
 * Auto-generated by easy-sdk
 */

{chr(10).join(interfaces)}
'''
    
    def _generate_interface(self, serializer: Dict, interface_name: str) -> str:
        """Generate a TypeScript interface from serializer"""
        fields = serializer.get('fields', {})
        field_definitions = []
        
        for field_name, field_info in fields.items():
            ts_type = self._get_typescript_type(field_info)
            optional = "?" if not field_info.get('required', True) else ""
            comment = f"  /** {field_info.get('help_text', '')} */" if field_info.get('help_text') else ""
            
            field_line = f"  {field_name}{optional}: {ts_type};"
            if comment:
                field_definitions.append(comment)
            field_definitions.append(field_line)
        
        docstring = serializer.get('docstring', f'{interface_name} data structure')
        
        return f'''/**
 * {docstring}
 */
export interface {interface_name} {{
{chr(10).join(field_definitions)}
}}'''
    
    def _get_typescript_type(self, field_info: Dict) -> str:
        """Get TypeScript type for a field"""
        field_type = field_info.get('type', 'string')
        allow_null = field_info.get('allow_null', False)
        
        # Map Django types to TypeScript types
        type_mapping = {
            'CharField': 'string',
            'TextField': 'string',
            'EmailField': 'string',
            'URLField': 'string',
            'SlugField': 'string',
            'UUIDField': 'string',
            'IntegerField': 'number',
            'BigIntegerField': 'number',
            'SmallIntegerField': 'number',
            'PositiveIntegerField': 'number',
            'FloatField': 'number',
            'DecimalField': 'number',
            'BooleanField': 'boolean',
            'DateField': 'string',
            'DateTimeField': 'string',
            'TimeField': 'string',
            'JSONField': 'Record<string, any>',
            'DictField': 'Record<string, any>',
            'ListField': 'any[]',
        }
        
        ts_type = type_mapping.get(field_type, 'string')
        
        # Handle choices
        if field_info.get('choices'):
            choices = [str(choice[0]) if isinstance(choice, (list, tuple)) else str(choice) 
                      for choice in field_info['choices']]
            ts_type = ' | '.join(f'"{choice}"' for choice in choices)
        
        # Handle nullable fields
        if allow_null:
            ts_type = f"{ts_type} | null"
        
        return ts_type
    
    def _generate_common_types(self, api_structure: Dict[str, Any]) -> str:
        """Generate common TypeScript types"""
        return '''/**
 * Common type definitions
 * Auto-generated by easy-sdk
 */

export interface APIResponse<T = any> {
  data?: T;
  message?: string;
  status: number;
}

export interface PaginatedResponse<T = any> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export interface QueryParams {
  [key: string]: string | number | boolean | undefined;
}

export interface ListParams extends QueryParams {
  page?: number;
  page_size?: number;
  ordering?: string;
  search?: string;
}

export interface ErrorResponse {
  message: string;
  errors?: Record<string, string[]>;
  detail?: string;
}
'''
    
    def _generate_types_index(self, api_structure: Dict[str, Any]) -> str:
        """Generate types index file"""
        exports = ['export * from "./common";']
        
        for app in api_structure['apps']:
            exports.append(f'export * from "./{app["name"]}";')
        
        return f'''/**
 * Type definitions index
 * Auto-generated by easy-sdk
 */

{chr(10).join(exports)}
'''
    
    def _generate_type_imports(self, operations: List[Dict]) -> str:
        """Generate type imports for client"""
        # Extract unique serializer types from operations
        types = set()
        for operation in operations:
            for endpoint in operation['endpoints']:
                serializer = endpoint.get('serializer_class', '')
                if serializer:
                    type_name = serializer.replace('Serializer', '')
                    types.add(type_name)
        
        return ', '.join(sorted(types))
    
    def _generate_client_methods(self, operations: List[Dict]) -> str:
        """Generate client methods for operations"""
        methods = []
        
        for operation in operations:
            for endpoint in operation['endpoints']:
                method_code = self._generate_method_code_ts(endpoint)
                methods.append(method_code)
        
        return '\n\n'.join(methods)
    
    def _generate_method_code_ts(self, endpoint: Dict) -> str:
        """Generate TypeScript code for a single API method"""
        method_name = self._generate_method_name_ts(endpoint)
        http_method = endpoint['method'].upper()
        path = endpoint['path']
        description = endpoint.get('description', f'{http_method} {path}')
        
        # Extract path parameters
        import re
        path_params = re.findall(r'\\{(\\w+)\\}', path)
        
        # Generate method signature
        params = []
        if path_params:
            params.extend([f"{param}: string | number" for param in path_params])
        
        # Add data parameter for POST/PUT/PATCH
        if http_method in ['POST', 'PUT', 'PATCH']:
            params.append("data?: any")
        
        # Add query parameters
        params.append("params?: QueryParams")
        
        param_str = ', '.join(params)
        if param_str:
            param_str = ', ' + param_str
        
        # Generate method body
        path_template = path
        for param in path_params:
            path_template = path_template.replace(f'{{{param}}}', f'${{{param}}}')
        
        if http_method in ['POST', 'PUT', 'PATCH']:
            request_call = f'return this.baseClient.{http_method.lower()}(`{path_template}`, data);'
        else:
            request_call = f'return this.baseClient.{http_method.lower()}(`{path_template}`, params);'
        
        return f'''  /**
   * {description}
   */
  async {method_name}({param_str.lstrip(', ')}): Promise<any> {{
    {request_call}
  }}'''
    
    def _generate_method_name_ts(self, endpoint: Dict) -> str:
        """Generate a TypeScript method name from endpoint"""
        method = endpoint['method'].lower()
        path = endpoint['path']
        
        # Extract resource and action
        path_parts = [p for p in path.split('/') if p and not p.startswith('{')]
        resource = path_parts[-1] if path_parts else 'resource'
        
        # Generate camelCase method names
        if method == 'get':
            if '{' in path:  # Detail endpoint
                return f"get{self._to_pascal_case(resource)}"
            else:  # List endpoint
                return f"list{self._to_pascal_case(resource)}"
        elif method == 'post':
            return f"create{self._to_pascal_case(resource)}"
        elif method == 'put':
            return f"update{self._to_pascal_case(resource)}"
        elif method == 'patch':
            return f"partialUpdate{self._to_pascal_case(resource)}"
        elif method == 'delete':
            return f"delete{self._to_pascal_case(resource)}"
        
        return f"{method}{self._to_pascal_case(resource)}"
    
    def _generate_client_imports(self, api_structure: Dict[str, Any]) -> str:
        """Generate imports for app clients"""
        imports = []
        for app in api_structure['apps']:
            class_name = f"{self._to_pascal_case(app['name'])}Client"
            imports.append(f"import {{ {class_name} }} from './clients/{class_name}';")
        
        return '\n'.join(imports)
    
    def _generate_client_properties(self, api_structure: Dict[str, Any]) -> str:
        """Generate client properties for each app"""
        properties = []
        for app in api_structure['apps']:
            app_name = app['name']
            class_name = f"{self._to_pascal_case(app_name)}Client"
            property_name = self._to_camel_case(app_name)
            
            properties.append(f"  public readonly {property_name}: {class_name};")
        
        return '\n'.join(properties)
    
    def _generate_client_initialization(self, api_structure: Dict[str, Any]) -> str:
        """Generate client initialization code"""
        initializations = []
        for app in api_structure['apps']:
            app_name = app['name']
            class_name = f"{self._to_pascal_case(app_name)}Client"
            property_name = self._to_camel_case(app_name)
            
            initializations.append(f"    this.{property_name} = new {class_name}(this.baseClient);")
        
        return '\n'.join(initializations)
    
    def _to_kebab_case(self, name: str) -> str:
        """Convert name to kebab-case"""
        return self._to_snake_case(name).replace('_', '-')
    
    def _to_pascal_case(self, name: str) -> str:
        """Convert name to PascalCase"""
        return self._to_class_name(name)
    
    def _to_camel_case(self, name: str) -> str:
        """Convert name to camelCase"""
        pascal = self._to_pascal_case(name)
        return pascal[0].lower() + pascal[1:] if pascal else ""