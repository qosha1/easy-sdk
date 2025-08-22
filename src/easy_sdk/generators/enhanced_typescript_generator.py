"""
Enhanced TypeScript generator with language template support and configurable naming conventions.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass

from ..core.config import DjangoDocsConfig
from ..utils.naming_conventions import (
    LanguageTemplate, LanguageConfig, get_language_config, 
    NamingConvention, NamingTransformer
)
from .language_templates import (
    FieldDefinition, InterfaceDefinition, 
    create_language_generator, generate_models_for_language
)

logger = logging.getLogger(__name__)


@dataclass
class TypeScriptGeneratorConfig:
    """Configuration for TypeScript generation"""
    language: LanguageTemplate = LanguageTemplate.TYPESCRIPT
    interface_naming: NamingConvention = NamingConvention.PASCAL_CASE
    property_naming: NamingConvention = NamingConvention.CAMEL_CASE
    preserve_django_names: bool = False  # Keep original Django field names
    generate_enums: bool = True
    generate_utility_types: bool = True
    strict_null_checks: bool = True
    readonly_fields: bool = True


class EnhancedTypeScriptGenerator:
    """
    Enhanced TypeScript generator with configurable naming conventions and language templates.
    """
    
    def __init__(self, config: DjangoDocsConfig, ts_config: Optional[TypeScriptGeneratorConfig] = None):
        self.config = config
        self.ts_config = ts_config or TypeScriptGeneratorConfig()
        self.output_dir = config.output.typescript_output_dir
        self.language_config = get_language_config(self.ts_config.language)
        
        # Apply custom naming conventions if specified
        if not self.ts_config.preserve_django_names:
            self.language_config.interface_naming = self.ts_config.interface_naming
            self.language_config.property_naming = self.ts_config.property_naming
        
        # Enhanced Django to TypeScript type mapping
        self.django_type_mapping = {
            # String types
            'CharField': 'string',
            'TextField': 'string', 
            'EmailField': 'string',
            'URLField': 'string',
            'SlugField': 'string',
            'UUIDField': 'string',
            
            # Numeric types
            'IntegerField': 'number',
            'BigIntegerField': 'number',
            'SmallIntegerField': 'number', 
            'PositiveIntegerField': 'number',
            'PositiveSmallIntegerField': 'number',
            'FloatField': 'number',
            'DecimalField': 'string',  # Keep as string to preserve precision
            
            # Boolean
            'BooleanField': 'boolean',
            'NullBooleanField': 'boolean',
            
            # Date/Time
            'DateTimeField': 'string',  # ISO 8601 format
            'DateField': 'string',     # YYYY-MM-DD format
            'TimeField': 'string',     # HH:MM:SS format
            
            # Complex types
            'JSONField': 'Record<string, any>',
            'DictField': 'Record<string, any>',
            'ListField': 'any[]',
            
            # File types
            'FileField': 'string',
            'ImageField': 'string',
            'FilePathField': 'string',
            
            # Relationship types
            'ForeignKey': 'number',
            'OneToOneField': 'number', 
            'ManyToManyField': 'number[]',
            
            # Choice fields
            'ChoiceField': 'string',  # Will be enhanced to union types
            'MultipleChoiceField': 'string[]',
            
            # DRF-specific fields
            'SerializerMethodField': 'any',
            'ReadOnlyField': 'any',
            'HiddenField': 'any',
            
            # Hyperlinked fields
            'HyperlinkedIdentityField': 'string',
            'HyperlinkedRelatedField': 'string',
            
            # Related fields
            'StringRelatedField': 'string',
            'SlugRelatedField': 'string',
            'PrimaryKeyRelatedField': 'number',
        }
        
        self.generated_interfaces: Dict[str, InterfaceDefinition] = {}
    
    def generate_types_from_analysis(self, analysis_results: Dict[str, Any]) -> List[Path]:
        """
        Generate TypeScript types from Django app analysis results.
        
        Args:
            analysis_results: Dictionary containing analysis results for all apps
            
        Returns:
            List of generated file paths
        """
        generated_files = []
        
        try:
            # Create output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Process each app's analysis
            app_interfaces = {}
            
            for app_name, app_data in analysis_results.items():
                if not app_data.get('serializers'):
                    continue
                
                interfaces = self._process_app_serializers(app_name, app_data['serializers'])
                app_interfaces[app_name] = interfaces
                logger.debug(f"Processed {len(interfaces)} interfaces for {app_name}")
            
            # Generate common utility types
            if self.ts_config.generate_utility_types:
                common_file = self._generate_common_types()
                generated_files.append(common_file)
            
            # Generate per-app type files
            for app_name, interfaces in app_interfaces.items():
                if interfaces:
                    app_file = self._generate_app_types_file(app_name, interfaces)
                    generated_files.append(app_file)
            
            # Generate main index file
            index_file = self._generate_index_file(list(app_interfaces.keys()))
            generated_files.append(index_file)
            
            total_interfaces = sum(len(interfaces) for interfaces in app_interfaces.values())
            logger.info(f"TypeScript generation complete: {len(generated_files)} files, {total_interfaces} interfaces")
            
        except Exception as e:
            logger.error(f"Failed to generate TypeScript types: {str(e)}")
            raise
        
        return generated_files
    
    def _process_app_serializers(self, app_name: str, serializers: List[Any]) -> List[InterfaceDefinition]:
        """Process serializers for an app and generate interface definitions"""
        interfaces = []
        
        for serializer in serializers:
            try:
                interface = self._serializer_to_interface(serializer)
                if interface:
                    interfaces.append(interface)
                    self.generated_interfaces[interface.name] = interface
                    
            except Exception as e:
                serializer_name = getattr(serializer, 'name', None) or str(serializer)
                logger.debug(f"Failed to process serializer {serializer_name} in app {app_name}: {str(e)}")
        
        return interfaces
    
    def _serializer_to_interface(self, serializer: Any) -> Optional[InterfaceDefinition]:
        """Convert a Django serializer to TypeScript interface definition"""
        if not hasattr(serializer, 'name'):
            return None
            
        serializer_name = serializer.name
        interface_name = self.language_config.transform_interface_name(serializer_name)
        
        fields = []
        
        # Process serializer fields
        if hasattr(serializer, 'fields') and serializer.fields:
            for field_name, field_info in serializer.fields.items():
                field_def = self._process_serializer_field(field_name, field_info)
                if field_def:
                    fields.append(field_def)
        
        # Generate interface
        interface = InterfaceDefinition(
            name=interface_name,
            fields=fields,
            description=f"Generated from {serializer_name} serializer"
        )
        
        return interface
    
    def _process_serializer_field(self, field_name: str, field_info: Any) -> Optional[FieldDefinition]:
        """Process a single serializer field"""
        try:
            # Get field type
            field_type = getattr(field_info, 'type', 'unknown')
            ts_type = self._map_django_type_to_typescript(field_type)
            
            # Transform field name according to naming convention
            if self.ts_config.preserve_django_names:
                prop_name = field_name
            else:
                prop_name = self.language_config.transform_property_name(field_name)
            
            # Determine field properties
            is_optional = getattr(field_info, 'required', True) == False
            is_readonly = getattr(field_info, 'read_only', False)
            is_nullable = getattr(field_info, 'allow_null', False)
            is_array = self._is_array_field(field_type)
            
            # Get description
            description = getattr(field_info, 'help_text', None)
            
            return FieldDefinition(
                name=prop_name,
                type_hint=ts_type,
                is_optional=is_optional,
                is_readonly=is_readonly and self.ts_config.readonly_fields,
                is_nullable=is_nullable and self.ts_config.strict_null_checks,
                is_array=is_array,
                description=description
            )
            
        except Exception as e:
            logger.warning(f"Failed to process field {field_name}: {str(e)}")
            return None
    
    def _map_django_type_to_typescript(self, django_type: str) -> str:
        """Map Django field type to TypeScript type"""
        return self.django_type_mapping.get(django_type, 'any')
    
    def _is_array_field(self, field_type: str) -> bool:
        """Check if field type represents an array"""
        array_types = {
            'ListField', 'ManyToManyField', 'MultipleChoiceField'
        }
        return field_type in array_types
    
    def _generate_common_types(self) -> Path:
        """Generate common utility types"""
        common_types = [
            InterfaceDefinition(
                name="PaginatedResponse",
                fields=[
                    FieldDefinition("results", "T[]", is_array=True),
                    FieldDefinition("count", "number"),
                    FieldDefinition("next", "string", is_nullable=True),
                    FieldDefinition("previous", "string", is_nullable=True),
                ],
                description="Standard Django REST framework paginated response"
            ),
            InterfaceDefinition(
                name="ApiError",
                fields=[
                    FieldDefinition("detail", "string", is_optional=True),
                    FieldDefinition("non_field_errors", "string[]", is_optional=True, is_array=True),
                ],
                description="API error response structure"
            )
        ]
        
        # Generate utility type aliases
        utility_definitions = '''
/**
 * Common utility type: Nullable
 */
export type Nullable<T> = T | null;

/**
 * Common utility type: Optional
 */
export type Optional<T> = T | undefined;

/**
 * Common utility type: Partial
 */
export type Partial<T> = Partial<T>;

/**
 * Common utility type: ApiResponse
 */
export type ApiResponse<T> = { data: T; message?: string; success: boolean };

/**
 * Supported HTTP methods
 */
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

'''
        
        # Generate interfaces using language template
        interfaces_content = generate_models_for_language(
            common_types,
            self.ts_config.language,
            "Common API types and utilities"
        )
        
        # Combine content
        content = interfaces_content + utility_definitions
        
        # Write to file
        common_file = self.output_dir / "common.d.ts"
        common_file.write_text(content)
        
        logger.debug(f"Generated common types: {common_file}")
        return common_file
    
    def _generate_app_types_file(self, app_name: str, interfaces: List[InterfaceDefinition]) -> Path:
        """Generate TypeScript file for an app's types"""
        
        # Transform app name for filename
        filename = self.language_config.transform_property_name(app_name)
        app_file = self.output_dir / f"{filename}.d.ts"
        
        # Generate content using language template
        content = generate_models_for_language(
            interfaces,
            self.ts_config.language,
            f"Generated types for {app_name} app"
        )
        
        # Add imports for common types
        if self.ts_config.generate_utility_types:
            imports = "import { PaginatedResponse, ApiError, Nullable, Optional } from './common';\n\n"
            content = imports + content
        
        # Write to file
        app_file.write_text(content)
        
        logger.debug(f"Generated {app_name} types: {app_file} ({len(interfaces)} interfaces)")
        return app_file
    
    def _generate_index_file(self, app_names: List[str]) -> Path:
        """Generate main index file that exports all types"""
        
        lines = [
            "/**",
            f" * Django API TypeScript Definitions",
            f" * Generated for Django API v{self.config.version or '1.0.0'}",
            " */",
            "",
            "// Common types and utilities"
        ]
        
        if self.ts_config.generate_utility_types:
            lines.append("export * from './common';")
            lines.append("")
        
        # Export app-specific types
        if app_names:
            lines.append("// App-specific types")
            for app_name in sorted(app_names):
                filename = self.language_config.transform_property_name(app_name)
                lines.append(f"export * from './{filename}';")
        else:
            lines.append("// Note: Add app exports here when generated")
        
        lines.append("")
        
        index_file = self.output_dir / "index.d.ts"
        index_file.write_text("\n".join(lines))
        
        logger.debug(f"Generated index file: {index_file}")
        return index_file


# Factory function for backward compatibility
def create_enhanced_typescript_generator(
    config: DjangoDocsConfig,
    interface_naming: NamingConvention = NamingConvention.PASCAL_CASE,
    property_naming: NamingConvention = NamingConvention.CAMEL_CASE,
    preserve_django_names: bool = False
) -> EnhancedTypeScriptGenerator:
    """Create enhanced TypeScript generator with custom naming conventions"""
    
    ts_config = TypeScriptGeneratorConfig(
        interface_naming=interface_naming,
        property_naming=property_naming,
        preserve_django_names=preserve_django_names
    )
    
    return EnhancedTypeScriptGenerator(config, ts_config)