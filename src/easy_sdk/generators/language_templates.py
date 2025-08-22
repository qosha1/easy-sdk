"""
Language-specific template generators for different programming languages.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from easy_sdk.utils.naming_conventions import (
    LanguageTemplate, LanguageConfig, get_language_config, NamingConvention
)


@dataclass
class FieldDefinition:
    """Represents a field in a data model"""
    name: str
    type_hint: str
    is_optional: bool = False
    is_readonly: bool = False
    is_array: bool = False
    is_nullable: bool = False
    default_value: Optional[str] = None
    description: Optional[str] = None


@dataclass 
class InterfaceDefinition:
    """Represents an interface/class definition"""
    name: str
    fields: List[FieldDefinition]
    description: Optional[str] = None
    extends: Optional[str] = None
    implements: List[str] = None


class LanguageGenerator(ABC):
    """Base class for language-specific generators"""
    
    def __init__(self, config: LanguageConfig):
        self.config = config
    
    @abstractmethod
    def generate_interface(self, interface: InterfaceDefinition) -> str:
        """Generate interface/class definition for this language"""
        pass
    
    @abstractmethod
    def generate_type_mapping(self, django_type: str) -> str:
        """Map Django field type to language-specific type"""
        pass
    
    def generate_file_header(self, description: str = "") -> str:
        """Generate file header with imports and comments"""
        return f"""/**
 * Generated API Types
 * {description}
 * 
 * This file was automatically generated. Do not edit manually.
 */

"""


class TypeScriptGenerator(LanguageGenerator):
    """Generate TypeScript interfaces"""
    
    TYPE_MAPPING = {
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
        'DecimalField': 'string',  # Keep as string to preserve precision
        'BooleanField': 'boolean',
        'DateTimeField': 'string',
        'DateField': 'string',
        'TimeField': 'string',
        'JSONField': 'any',
        'ForeignKey': 'number',
        'OneToOneField': 'number',
        'ManyToManyField': 'number[]',
        'ImageField': 'string',
        'FileField': 'string',
    }
    
    def generate_interface(self, interface: InterfaceDefinition) -> str:
        """Generate TypeScript interface"""
        interface_name = self.config.transform_interface_name(interface.name)
        
        lines = []
        
        # Add description if provided
        if interface.description:
            lines.append(f"/**\n * {interface.description}\n */")
        
        # Interface declaration
        extends_clause = f" extends {interface.extends}" if interface.extends else ""
        lines.append(f"{self.config.export_keyword} {self.config.interface_keyword} {interface_name}{extends_clause} {{")
        
        # Generate fields
        for field in interface.fields:
            field_line = self._generate_field(field)
            lines.append(f"  {field_line}")
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def _generate_field(self, field: FieldDefinition) -> str:
        """Generate a single field definition"""
        prop_name = self.config.transform_property_name(field.name)
        
        # Build type string
        type_str = field.type_hint
        
        if field.is_array:
            type_str += self.config.array_syntax
        
        if field.is_nullable:
            type_str += self.config.nullable_syntax
        
        # Optional marker
        optional_marker = self.config.optional_syntax if field.is_optional else ""
        
        # Readonly modifier
        readonly = self.config.readonly_syntax if field.is_readonly else ""
        
        # Build complete field definition
        field_def = f"{readonly}{prop_name}{optional_marker}: {type_str};"
        
        # Add description comment if provided
        if field.description:
            field_def = f"/** {field.description} */ {field_def}"
        
        return field_def
    
    def generate_type_mapping(self, django_type: str) -> str:
        """Map Django field type to TypeScript type"""
        return self.TYPE_MAPPING.get(django_type, 'any')


class PythonGenerator(LanguageGenerator):
    """Generate Python dataclasses/Pydantic models"""
    
    TYPE_MAPPING = {
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
        'DecimalField': 'Decimal',
        'BooleanField': 'bool',
        'DateTimeField': 'datetime',
        'DateField': 'date',
        'TimeField': 'time',
        'JSONField': 'Dict[str, Any]',
        'ForeignKey': 'int',
        'OneToOneField': 'int',
        'ManyToManyField': 'List[int]',
        'ImageField': 'str',
        'FileField': 'str',
    }
    
    def generate_file_header(self, description: str = "") -> str:
        """Generate Python file header with imports"""
        return f'''"""
Generated API Types
{description}

This file was automatically generated. Do not edit manually.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime, date, time
from decimal import Decimal

'''
    
    def generate_interface(self, interface: InterfaceDefinition) -> str:
        """Generate Python dataclass"""
        class_name = self.config.transform_interface_name(interface.name)
        
        lines = []
        
        # Add description if provided
        if interface.description:
            lines.append(f'"""{interface.description}"""')
        
        # Class declaration
        lines.append("@dataclass")
        base_class = f"({interface.extends})" if interface.extends else ""
        lines.append(f"class {class_name}{base_class}:")
        
        # Add docstring
        if interface.description:
            lines.append(f'    """{interface.description}"""')
        
        # Generate fields
        if not interface.fields:
            lines.append("    pass")
        else:
            for field in interface.fields:
                field_line = self._generate_field(field)
                lines.append(f"    {field_line}")
        
        return "\n".join(lines)
    
    def _generate_field(self, field: FieldDefinition) -> str:
        """Generate a single field definition"""
        prop_name = self.config.transform_property_name(field.name)
        
        # Build type string
        type_str = field.type_hint
        
        if field.is_array:
            type_str = f"List[{type_str}]"
        
        if field.is_nullable or field.is_optional:
            type_str = f"Optional[{type_str}]"
        
        # Default value
        default = " = None" if (field.is_optional or field.is_nullable) else ""
        if field.default_value:
            default = f" = {field.default_value}"
        
        return f"{prop_name}: {type_str}{default}"
    
    def generate_type_mapping(self, django_type: str) -> str:
        """Map Django field type to Python type"""
        return self.TYPE_MAPPING.get(django_type, 'Any')


class JavaGenerator(LanguageGenerator):
    """Generate Java classes"""
    
    TYPE_MAPPING = {
        'CharField': 'String',
        'TextField': 'String', 
        'EmailField': 'String',
        'URLField': 'String',
        'SlugField': 'String',
        'UUIDField': 'String',
        'IntegerField': 'Integer',
        'BigIntegerField': 'Long',
        'SmallIntegerField': 'Integer',
        'PositiveIntegerField': 'Integer',
        'FloatField': 'Double',
        'DecimalField': 'BigDecimal',
        'BooleanField': 'Boolean',
        'DateTimeField': 'LocalDateTime',
        'DateField': 'LocalDate',
        'TimeField': 'LocalTime',
        'JSONField': 'Object',
        'ForeignKey': 'Long',
        'OneToOneField': 'Long',
        'ManyToManyField': 'List<Long>',
        'ImageField': 'String',
        'FileField': 'String',
    }
    
    def generate_file_header(self, description: str = "") -> str:
        """Generate Java file header with imports"""
        return f'''/**
 * Generated API Types
 * {description}
 * 
 * This file was automatically generated. Do not edit manually.
 */

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.LocalDate;
import java.time.LocalTime;
import java.util.List;

'''
    
    def generate_interface(self, interface: InterfaceDefinition) -> str:
        """Generate Java class"""
        class_name = self.config.transform_interface_name(interface.name)
        
        lines = []
        
        # Add description if provided
        if interface.description:
            lines.append(f"/**\n * {interface.description}\n */")
        
        # Class declaration
        extends_clause = f" extends {interface.extends}" if interface.extends else ""
        lines.append(f"public class {class_name}{extends_clause} {{")
        
        # Generate fields
        for field in interface.fields:
            field_lines = self._generate_field(field)
            for line in field_lines:
                lines.append(f"    {line}")
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def _generate_field(self, field: FieldDefinition) -> List[str]:
        """Generate field with getter/setter"""
        prop_name = self.config.transform_property_name(field.name)
        type_str = field.type_hint
        
        if field.is_array:
            type_str = f"List<{type_str}>"
        
        lines = []
        
        # Field declaration
        if field.description:
            lines.append(f"/** {field.description} */")
        
        lines.append(f"private {type_str} {prop_name};")
        lines.append("")
        
        # Getter
        getter_name = f"get{prop_name.capitalize()}"
        lines.append(f"public {type_str} {getter_name}() {{")
        lines.append(f"    return {prop_name};")
        lines.append("}")
        lines.append("")
        
        # Setter
        setter_name = f"set{prop_name.capitalize()}"
        lines.append(f"public void {setter_name}({type_str} {prop_name}) {{")
        lines.append(f"    this.{prop_name} = {prop_name};")
        lines.append("}")
        lines.append("")
        
        return lines
    
    def generate_type_mapping(self, django_type: str) -> str:
        """Map Django field type to Java type"""
        return self.TYPE_MAPPING.get(django_type, 'Object')


# Factory for creating language generators
def create_language_generator(language: LanguageTemplate) -> LanguageGenerator:
    """Create appropriate language generator"""
    config = get_language_config(language)
    
    generators = {
        LanguageTemplate.TYPESCRIPT: TypeScriptGenerator,
        LanguageTemplate.PYTHON: PythonGenerator,
        LanguageTemplate.JAVA: JavaGenerator,
        # Add more generators as needed
    }
    
    generator_class = generators.get(language, TypeScriptGenerator)
    return generator_class(config)


def generate_models_for_language(
    interfaces: List[InterfaceDefinition],
    language: LanguageTemplate,
    description: str = ""
) -> str:
    """Generate model definitions for a specific language"""
    generator = create_language_generator(language)
    
    output = [generator.generate_file_header(description)]
    
    for interface in interfaces:
        output.append(generator.generate_interface(interface))
        output.append("\n")  # Add spacing between interfaces
    
    return "\n".join(output)