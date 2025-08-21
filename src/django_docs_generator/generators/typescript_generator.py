"""
TypeScript interface generator for Django API types
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..core.config import DjangoDocsConfig

logger = logging.getLogger(__name__)


class TypeScriptType:
    """Represents a TypeScript type definition"""
    
    def __init__(self, name: str, type_definition: str):
        self.name = name
        self.type_definition = type_definition
        self.dependencies: Set[str] = set()
        self.is_interface = False
        self.is_enum = False
        self.description = ""
        self.properties: Dict[str, str] = {}
        self.export = True
    
    def add_dependency(self, dependency: str) -> None:
        """Add a type dependency"""
        self.dependencies.add(dependency)
    
    def to_typescript(self) -> str:
        """Generate TypeScript code for this type"""
        if self.is_interface:
            return self._generate_interface()
        elif self.is_enum:
            return self._generate_enum()
        else:
            return self._generate_type_alias()
    
    def _generate_interface(self) -> str:
        """Generate TypeScript interface"""
        lines = []
        
        if self.description:
            lines.append(f"/**\n * {self.description}\n */")
        
        export_prefix = "export " if self.export else ""
        lines.append(f"{export_prefix}interface {self.name} {{")
        
        for prop_name, prop_type in self.properties.items():
            lines.append(f"  {prop_name}: {prop_type};")
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def _generate_enum(self) -> str:
        """Generate TypeScript enum"""
        lines = []
        
        if self.description:
            lines.append(f"/**\n * {self.description}\n */")
        
        export_prefix = "export " if self.export else ""
        lines.append(f"{export_prefix}enum {self.name} {{")
        
        # Properties for enums are key-value pairs
        for key, value in self.properties.items():
            lines.append(f"  {key} = {value},")
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def _generate_type_alias(self) -> str:
        """Generate TypeScript type alias"""
        lines = []
        
        if self.description:
            lines.append(f"/**\n * {self.description}\n */")
        
        export_prefix = "export " if self.export else ""
        lines.append(f"{export_prefix}type {self.name} = {self.type_definition};")
        
        return "\n".join(lines)


class TypeScriptGenerator:
    """
    Generates TypeScript type definitions from Django serializer analysis
    """
    
    def __init__(self, config: DjangoDocsConfig):
        self.config = config
        self.output_dir = config.output.typescript_output_dir
        
        # Type mapping from Django/DRF types to TypeScript
        self.type_mapping = {
            'string': 'string',
            'integer': 'number',
            'float': 'number',
            'decimal': 'number',
            'boolean': 'boolean',
            'date': 'string',
            'datetime': 'string',
            'time': 'string',
            'email': 'string',
            'url': 'string',
            'uuid': 'string',
            'slug': 'string',
            'json': 'Record<string, any>',
            'object': 'Record<string, any>',
            'list': 'any[]',
            'choice': 'string',  # Will be enhanced to union types
            'file': 'File | string',
            'image': 'File | string',
            'read_only': 'string',
            'method': 'any',  # SerializerMethodField
            'primary_key': 'number | string',
            'hyperlink_identity': 'string',
            'hyperlink_related': 'string',
            'string_related': 'string',
            'slug_related': 'string',
        }
        
        # Common TypeScript utility types
        self.utility_types = {
            'Nullable': 'T | null',
            'Optional': 'T | undefined',
            'Partial': 'Partial<T>',
            'ApiResponse': '{ data: T; message?: string; success: boolean }',
            'PaginatedResponse': '{ results: T[]; count: number; next?: string; previous?: string }',
            'ValidationError': '{ field?: string; message: string; code?: string }',
        }
    
    def generate_types(self) -> List[Path]:
        """
        Generate TypeScript type definitions
        
        Returns:
            List of generated file paths
        """
        generated_files = []
        
        try:
            # Create output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate common types
            common_file = self._generate_common_types()
            generated_files.append(common_file)
            
            # Generate app-specific types
            # Note: This would use analysis results passed to the method
            # For now, creating placeholder structure
            app_files = self._generate_app_types()
            generated_files.extend(app_files)
            
            # Generate main index file
            index_file = self._generate_index_file()
            generated_files.append(index_file)
            
            logger.info(f"Generated {len(generated_files)} TypeScript definition files")
            
        except Exception as e:
            logger.error(f"Failed to generate TypeScript types: {str(e)}")
        
        return generated_files
    
    def generate_app_types(self, app_name: str, app_analysis: Dict[str, Any]) -> Path:
        """
        Generate TypeScript types for a specific Django app
        
        Args:
            app_name: Name of the Django app
            app_analysis: Analysis results for the app
            
        Returns:
            Path to generated TypeScript file
        """
        try:
            types = []
            
            # Generate types from serializers
            if 'serializers' in app_analysis:
                serializer_types = self._generate_serializer_types(
                    app_analysis['serializers']
                )
                types.extend(serializer_types)
            
            # Generate endpoint request/response types
            if 'views' in app_analysis:
                endpoint_types = self._generate_endpoint_types(
                    app_analysis['views']
                )
                types.extend(endpoint_types)
            
            # Generate the TypeScript file
            output_file = self.output_dir / f"{app_name}.d.ts"
            content = self._generate_typescript_file(f"{app_name} API Types", types)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Generated TypeScript types for app '{app_name}': {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to generate TypeScript types for app {app_name}: {str(e)}")
            raise
    
    def _generate_common_types(self) -> Path:
        """Generate common TypeScript types used across all apps"""
        types = []
        
        # Generate utility types
        for name, definition in self.utility_types.items():
            ts_type = TypeScriptType(name, definition)
            ts_type.description = f"Common utility type: {name}"
            types.append(ts_type)
        
        # Generate common Django/DRF response types
        pagination_type = TypeScriptType("PaginatedResponse", "")
        pagination_type.is_interface = True
        pagination_type.description = "Standard Django REST framework paginated response"
        pagination_type.properties = {
            "results": "T[]",
            "count": "number",
            "next": "string | null",
            "previous": "string | null"
        }
        types.append(pagination_type)
        
        # API Error type
        error_type = TypeScriptType("ApiError", "")
        error_type.is_interface = True
        error_type.description = "API error response structure"
        error_type.properties = {
            "detail?": "string",
            "non_field_errors?": "string[]",
            "[field: string]": "string[] | string"
        }
        types.append(error_type)
        
        # HTTP method type
        http_method_type = TypeScriptType("HttpMethod", "'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'")
        http_method_type.description = "Supported HTTP methods"
        types.append(http_method_type)
        
        # Generate file
        output_file = self.output_dir / "common.d.ts"
        content = self._generate_typescript_file("Common API Types", types)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_file
    
    def _generate_app_types(self) -> List[Path]:
        """Generate types for all apps (placeholder)"""
        # This would iterate through analyzed apps in real implementation
        return []
    
    def _generate_serializer_types(self, serializers: List[Dict[str, Any]]) -> List[TypeScriptType]:
        """Generate TypeScript interfaces from Django serializers"""
        types = []
        
        for serializer in serializers:
            try:
                ts_type = self._convert_serializer_to_interface(serializer)
                if ts_type:
                    types.append(ts_type)
                
                # Generate related types (create, update variants)
                related_types = self._generate_serializer_variants(serializer)
                types.extend(related_types)
                
            except Exception as e:
                logger.warning(f"Failed to generate type for serializer {serializer.get('name', 'unknown')}: {str(e)}")
        
        return types
    
    def _convert_serializer_to_interface(self, serializer: Dict[str, Any]) -> Optional[TypeScriptType]:
        """Convert a Django serializer to TypeScript interface"""
        try:
            name = serializer.get('name', '')
            if not name:
                return None
            
            ts_type = TypeScriptType(name, "")
            ts_type.is_interface = True
            ts_type.description = serializer.get('docstring', f"Interface for {name} serializer")
            
            # Process fields
            fields = serializer.get('fields', {})
            for field_name, field_info in fields.items():
                ts_field_type = self._convert_field_to_typescript(field_info)
                
                # Handle optional/required fields
                if not field_info.get('required', True) or field_info.get('read_only', False):
                    field_name += '?'
                
                ts_type.properties[field_name] = ts_field_type
                
                # Track dependencies
                if 'nested_serializer' in field_info:
                    ts_type.add_dependency(field_info['nested_serializer'])
            
            return ts_type
            
        except Exception as e:
            logger.warning(f"Failed to convert serializer to interface: {str(e)}")
            return None
    
    def _convert_field_to_typescript(self, field_info: Dict[str, Any]) -> str:
        """Convert a Django serializer field to TypeScript type"""
        try:
            field_type = field_info.get('type', 'any')
            
            # Use AI-inferred type if available
            if 'typescript_type' in field_info:
                return field_info['typescript_type']
            
            # Handle choices - create union types
            if field_info.get('choices'):
                choices = field_info['choices']
                if isinstance(choices, list) and choices:
                    # Create union type from choices
                    choice_values = []
                    for choice in choices:
                        if isinstance(choice, (list, tuple)) and len(choice) >= 2:
                            # Django choice format: (value, display_name)
                            value = choice[0]
                            if isinstance(value, str):
                                choice_values.append(f"'{value}'")
                            else:
                                choice_values.append(str(value))
                    
                    if choice_values:
                        return " | ".join(choice_values)
            
            # Handle list types
            if field_type == 'list' or field_type.startswith('list_'):
                child_type = field_type.replace('list_', '') if field_type.startswith('list_') else 'any'
                child_ts_type = self.type_mapping.get(child_type, child_type)
                return f"{child_ts_type}[]"
            
            # Handle nested serializers
            if field_info.get('nested_serializer'):
                nested_name = field_info['nested_serializer']
                if field_type.startswith('list_'):
                    return f"{nested_name}[]"
                else:
                    return nested_name
            
            # Handle related fields
            if field_info.get('related_model'):
                model_name = field_info['related_model']
                if field_type.startswith('list_'):
                    return f"{model_name}[]"
                else:
                    # For foreign keys, typically return the ID type
                    return "number | string"
            
            # Handle nullable fields
            base_type = self.type_mapping.get(field_type, 'any')
            
            if field_info.get('allow_null'):
                base_type = f"{base_type} | null"
            
            return base_type
            
        except Exception as e:
            logger.warning(f"Failed to convert field type: {str(e)}")
            return 'any'
    
    def _generate_serializer_variants(self, serializer: Dict[str, Any]) -> List[TypeScriptType]:
        """Generate create/update/partial variants of serializer interfaces"""
        variants = []
        
        try:
            name = serializer.get('name', '')
            if not name:
                return variants
            
            base_name = name.replace('Serializer', '')
            
            # Generate CreateXXX interface (without read-only fields)
            create_type = TypeScriptType(f"Create{base_name}", "")
            create_type.is_interface = True
            create_type.description = f"Interface for creating {base_name} objects"
            
            # Generate UpdateXXX interface (partial, without read-only fields)
            update_type = TypeScriptType(f"Update{base_name}", "")
            update_type.is_interface = True
            update_type.description = f"Interface for updating {base_name} objects"
            
            fields = serializer.get('fields', {})
            for field_name, field_info in fields.items():
                # Skip read-only fields for create/update
                if field_info.get('read_only', False):
                    continue
                
                ts_field_type = self._convert_field_to_typescript(field_info)
                
                # Create interface - required fields stay required
                create_field_name = field_name
                if not field_info.get('required', True):
                    create_field_name += '?'
                create_type.properties[create_field_name] = ts_field_type
                
                # Update interface - all fields become optional
                update_field_name = field_name + '?'
                update_type.properties[update_field_name] = ts_field_type
            
            if create_type.properties:
                variants.append(create_type)
            
            if update_type.properties:
                variants.append(update_type)
                
        except Exception as e:
            logger.warning(f"Failed to generate serializer variants: {str(e)}")
        
        return variants
    
    def _generate_endpoint_types(self, views: List[Dict[str, Any]]) -> List[TypeScriptType]:
        """Generate types for API endpoints"""
        types = []
        
        for view in views:
            try:
                view_name = view.get('name', '')
                endpoints = view.get('endpoints', [])
                
                for endpoint in endpoints:
                    endpoint_types = self._generate_endpoint_type_variants(view_name, endpoint)
                    types.extend(endpoint_types)
                    
            except Exception as e:
                logger.warning(f"Failed to generate endpoint types for view {view.get('name', 'unknown')}: {str(e)}")
        
        return types
    
    def _generate_endpoint_type_variants(self, view_name: str, endpoint: Dict[str, Any]) -> List[TypeScriptType]:
        """Generate request/response types for an endpoint"""
        types = []
        
        try:
            method = endpoint.get('method', 'GET').upper()
            function_name = endpoint.get('function_name', method.lower())
            
            # Generate request type for POST/PUT/PATCH
            if method in ['POST', 'PUT', 'PATCH']:
                request_type_name = f"{view_name}{function_name.title()}Request"
                request_type = TypeScriptType(request_type_name, "")
                request_type.is_interface = True
                request_type.description = f"Request payload for {method} {endpoint.get('path', '')}"
                
                # Use serializer class as base if available
                serializer_class = endpoint.get('serializer_class')
                if serializer_class:
                    if method == 'POST':
                        request_type.type_definition = f"Create{serializer_class.replace('Serializer', '')}"
                    else:
                        request_type.type_definition = f"Update{serializer_class.replace('Serializer', '')}"
                    request_type.is_interface = False
                else:
                    request_type.properties = {"[key: string]": "any"}
                
                types.append(request_type)
            
            # Generate response type
            response_type_name = f"{view_name}{function_name.title()}Response"
            response_type = TypeScriptType(response_type_name, "")
            response_type.is_interface = True
            response_type.description = f"Response for {method} {endpoint.get('path', '')}"
            
            # Determine response structure
            serializer_class = endpoint.get('serializer_class')
            if serializer_class:
                base_type = serializer_class.replace('Serializer', '')
                if method == 'GET' and 'list' in function_name.lower():
                    # List endpoint - return paginated response
                    response_type.type_definition = f"PaginatedResponse<{base_type}>"
                    response_type.is_interface = False
                else:
                    # Single object response
                    response_type.type_definition = base_type
                    response_type.is_interface = False
            else:
                response_type.properties = {"[key: string]": "any"}
            
            types.append(response_type)
            
        except Exception as e:
            logger.warning(f"Failed to generate endpoint type variants: {str(e)}")
        
        return types
    
    def _generate_index_file(self) -> Path:
        """Generate main index.d.ts file that exports all types"""
        try:
            lines = [
                "/**",
                " * Django API TypeScript Definitions",
                f" * Generated for {self.config.project_name} v{self.config.version}",
                " */",
                "",
                "// Common types and utilities",
                "export * from './common';",
                "",
                "// App-specific types",
                "// Note: Add app exports here when generated",
                "",
            ]
            
            content = "\n".join(lines)
            
            index_file = self.output_dir / "index.d.ts"
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return index_file
            
        except Exception as e:
            logger.error(f"Failed to generate index file: {str(e)}")
            raise
    
    def _generate_typescript_file(self, title: str, types: List[TypeScriptType]) -> str:
        """Generate complete TypeScript definition file"""
        lines = [
            "/**",
            f" * {title}",
            f" * Generated for {self.config.project_name}",
            " */",
            "",
        ]
        
        # Add imports for dependencies
        all_dependencies = set()
        for ts_type in types:
            all_dependencies.update(ts_type.dependencies)
        
        if all_dependencies:
            lines.append("// Type dependencies")
            for dep in sorted(all_dependencies):
                lines.append(f"import {{ {dep} }} from './{dep}';")
            lines.append("")
        
        # Add type definitions
        for ts_type in types:
            lines.append(ts_type.to_typescript())
            lines.append("")
        
        return "\n".join(lines)
    
    def get_typescript_type_for_field(self, field_info: Dict[str, Any]) -> str:
        """Public method to get TypeScript type for a field"""
        return self._convert_field_to_typescript(field_info)