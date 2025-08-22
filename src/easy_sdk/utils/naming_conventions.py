"""
Naming convention utilities for different programming languages and styles.
"""

import re
from enum import Enum
from typing import Dict, Callable


class NamingConvention(Enum):
    """Supported naming conventions"""
    SNAKE_CASE = "snake_case"           # user_profile, order_item
    CAMEL_CASE = "camelCase"            # userProfile, orderItem  
    PASCAL_CASE = "PascalCase"          # UserProfile, OrderItem
    KEBAB_CASE = "kebab-case"           # user-profile, order-item
    SCREAMING_SNAKE = "SCREAMING_SNAKE" # USER_PROFILE, ORDER_ITEM
    LOWER_CASE = "lowercase"            # userprofile, orderitem


class LanguageTemplate(Enum):
    """Supported language templates"""
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    PYTHON = "python"
    JAVA = "java"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    SWIFT = "swift"
    KOTLIN = "kotlin"


class NamingTransformer:
    """Transform strings between different naming conventions"""
    
    @staticmethod
    def to_snake_case(text: str) -> str:
        """Convert to snake_case"""
        # Handle camelCase and PascalCase
        text = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', text)
        # Handle kebab-case
        text = text.replace('-', '_')
        # Handle spaces
        text = text.replace(' ', '_')
        # Convert to lowercase and remove multiple underscores
        return re.sub(r'_+', '_', text.lower()).strip('_')
    
    @staticmethod
    def to_camel_case(text: str) -> str:
        """Convert to camelCase"""
        snake = NamingTransformer.to_snake_case(text)
        components = snake.split('_')
        return components[0].lower() + ''.join(word.capitalize() for word in components[1:])
    
    @staticmethod
    def to_pascal_case(text: str) -> str:
        """Convert to PascalCase"""
        snake = NamingTransformer.to_snake_case(text)
        components = snake.split('_')
        return ''.join(word.capitalize() for word in components)
    
    @staticmethod
    def to_kebab_case(text: str) -> str:
        """Convert to kebab-case"""
        return NamingTransformer.to_snake_case(text).replace('_', '-')
    
    @staticmethod
    def to_screaming_snake(text: str) -> str:
        """Convert to SCREAMING_SNAKE_CASE"""
        return NamingTransformer.to_snake_case(text).upper()
    
    @staticmethod
    def to_lower_case(text: str) -> str:
        """Convert to lowercase (no separators)"""
        return NamingTransformer.to_snake_case(text).replace('_', '').lower()


class LanguageConfig:
    """Configuration for language-specific formatting"""
    
    def __init__(
        self,
        language: LanguageTemplate,
        interface_naming: NamingConvention = NamingConvention.PASCAL_CASE,
        property_naming: NamingConvention = NamingConvention.CAMEL_CASE,
        type_suffix: str = "",
        nullable_syntax: str = " | null",
        array_syntax: str = "[]",
        optional_syntax: str = "?",
        readonly_syntax: str = "readonly ",
        interface_keyword: str = "interface",
        export_keyword: str = "export",
    ):
        self.language = language
        self.interface_naming = interface_naming
        self.property_naming = property_naming
        self.type_suffix = type_suffix
        self.nullable_syntax = nullable_syntax
        self.array_syntax = array_syntax
        self.optional_syntax = optional_syntax
        self.readonly_syntax = readonly_syntax
        self.interface_keyword = interface_keyword
        self.export_keyword = export_keyword
    
    def transform_interface_name(self, name: str) -> str:
        """Transform interface name according to convention"""
        return self._apply_naming_convention(name, self.interface_naming) + self.type_suffix
    
    def transform_property_name(self, name: str) -> str:
        """Transform property name according to convention"""
        return self._apply_naming_convention(name, self.property_naming)
    
    def _apply_naming_convention(self, text: str, convention: NamingConvention) -> str:
        """Apply naming convention transformation"""
        transformers: Dict[NamingConvention, Callable[[str], str]] = {
            NamingConvention.SNAKE_CASE: NamingTransformer.to_snake_case,
            NamingConvention.CAMEL_CASE: NamingTransformer.to_camel_case,
            NamingConvention.PASCAL_CASE: NamingTransformer.to_pascal_case,
            NamingConvention.KEBAB_CASE: NamingTransformer.to_kebab_case,
            NamingConvention.SCREAMING_SNAKE: NamingTransformer.to_screaming_snake,
            NamingConvention.LOWER_CASE: NamingTransformer.to_lower_case,
        }
        
        transformer = transformers.get(convention, lambda x: x)
        return transformer(text)


# Predefined language configurations
LANGUAGE_CONFIGS: Dict[LanguageTemplate, LanguageConfig] = {
    LanguageTemplate.TYPESCRIPT: LanguageConfig(
        language=LanguageTemplate.TYPESCRIPT,
        interface_naming=NamingConvention.PASCAL_CASE,
        property_naming=NamingConvention.CAMEL_CASE,
        nullable_syntax=" | null",
        array_syntax="[]",
        optional_syntax="?",
        interface_keyword="interface",
        export_keyword="export",
    ),
    
    LanguageTemplate.JAVASCRIPT: LanguageConfig(
        language=LanguageTemplate.JAVASCRIPT,
        interface_naming=NamingConvention.PASCAL_CASE,
        property_naming=NamingConvention.CAMEL_CASE,
        type_suffix="",
        nullable_syntax="",  # JS doesn't have explicit null types
        array_syntax="",
        optional_syntax="",
        interface_keyword="class",  # Use class for JS
        export_keyword="export",
    ),
    
    LanguageTemplate.PYTHON: LanguageConfig(
        language=LanguageTemplate.PYTHON,
        interface_naming=NamingConvention.PASCAL_CASE,
        property_naming=NamingConvention.SNAKE_CASE,
        nullable_syntax=" | None",
        array_syntax="List",
        optional_syntax="Optional",
        interface_keyword="class",
        export_keyword="",
    ),
    
    LanguageTemplate.JAVA: LanguageConfig(
        language=LanguageTemplate.JAVA,
        interface_naming=NamingConvention.PASCAL_CASE,
        property_naming=NamingConvention.CAMEL_CASE,
        type_suffix="",
        nullable_syntax="",  # Java uses @Nullable annotation
        array_syntax="[]",
        optional_syntax="",
        interface_keyword="public class",
        export_keyword="public",
    ),
    
    LanguageTemplate.CSHARP: LanguageConfig(
        language=LanguageTemplate.CSHARP,
        interface_naming=NamingConvention.PASCAL_CASE,
        property_naming=NamingConvention.PASCAL_CASE,
        type_suffix="",
        nullable_syntax="?",
        array_syntax="[]",
        optional_syntax="?",
        interface_keyword="public class",
        export_keyword="public",
    ),
    
    LanguageTemplate.GO: LanguageConfig(
        language=LanguageTemplate.GO,
        interface_naming=NamingConvention.PASCAL_CASE,
        property_naming=NamingConvention.PASCAL_CASE,
        type_suffix="",
        nullable_syntax="*",  # Go uses pointers for nullable
        array_syntax="[]",
        optional_syntax="",
        interface_keyword="type",
        export_keyword="",
    ),
    
    LanguageTemplate.RUST: LanguageConfig(
        language=LanguageTemplate.RUST,
        interface_naming=NamingConvention.PASCAL_CASE,
        property_naming=NamingConvention.SNAKE_CASE,
        type_suffix="",
        nullable_syntax="Option<>",
        array_syntax="Vec<>",
        optional_syntax="",
        interface_keyword="struct",
        export_keyword="pub",
    ),
    
    LanguageTemplate.SWIFT: LanguageConfig(
        language=LanguageTemplate.SWIFT,
        interface_naming=NamingConvention.PASCAL_CASE,
        property_naming=NamingConvention.CAMEL_CASE,
        type_suffix="",
        nullable_syntax="?",
        array_syntax="[]",
        optional_syntax="?",
        interface_keyword="struct",
        export_keyword="public",
    ),
    
    LanguageTemplate.KOTLIN: LanguageConfig(
        language=LanguageTemplate.KOTLIN,
        interface_naming=NamingConvention.PASCAL_CASE,
        property_naming=NamingConvention.CAMEL_CASE,
        type_suffix="",
        nullable_syntax="?",
        array_syntax="Array",
        optional_syntax="?",
        interface_keyword="data class",
        export_keyword="",
    ),
}


def get_language_config(language: LanguageTemplate) -> LanguageConfig:
    """Get language configuration for a specific language"""
    return LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS[LanguageTemplate.TYPESCRIPT])


def get_available_languages() -> list[str]:
    """Get list of available language templates"""
    return [lang.value for lang in LanguageTemplate]


def get_available_naming_conventions() -> list[str]:
    """Get list of available naming conventions"""
    return [conv.value for conv in NamingConvention]