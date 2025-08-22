"""
Multi-language generator that creates type definitions in multiple programming languages
with configurable naming conventions.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass

from ..core.config import DjangoDocsConfig
from ..utils.naming_conventions import LanguageTemplate, NamingConvention
from .enhanced_typescript_generator import EnhancedTypeScriptGenerator, TypeScriptGeneratorConfig
from .language_templates import create_language_generator, generate_models_for_language, InterfaceDefinition, FieldDefinition

logger = logging.getLogger(__name__)


class MultiLanguageGenerator:
    """
    Multi-language generator that creates type definitions in multiple programming 
    languages with multiple naming convention variants.
    """
    
    def __init__(self, config: DjangoDocsConfig):
        self.config = config
        self.output_base_dir = config.output.typescript_output_dir.parent / "types_multi"
        
        # Parse configuration
        self.primary_language = config.generation.language_template
        self.primary_interface_naming = config.generation.interface_naming_convention
        self.primary_property_naming = config.generation.property_naming_convention
        self.preserve_django_names = config.generation.preserve_django_field_names
        
        # Languages to generate
        self.languages = [self.primary_language]
        if config.generation.generate_multiple_languages:
            self.languages.extend(config.generation.additional_languages)
            
        # Naming variants to generate
        self.naming_variants = [(self.primary_interface_naming, self.primary_property_naming)]
        if config.generation.generate_all_naming_variants:
            # Create combinations of naming conventions
            for interface_naming in config.generation.naming_variants:
                for property_naming in config.generation.naming_variants:
                    variant = (interface_naming, property_naming)
                    if variant not in self.naming_variants:
                        self.naming_variants.append(variant)
        
        logger.info(f"Multi-language generator: {len(self.languages)} languages, {len(self.naming_variants)} naming variants")
    
    def generate_types_from_analysis(self, analysis_results: Dict[str, Any]) -> List[Path]:
        """
        Generate type definitions for all languages and naming variants.
        
        Args:
            analysis_results: Dictionary containing analysis results for all apps
            
        Returns:
            List of generated file paths
        """
        generated_files = []
        
        try:
            # Create output directory
            self.output_base_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate for each language
            for language in self.languages:
                language_files = self._generate_for_language(language, analysis_results)
                generated_files.extend(language_files)
            
            # Generate master index file
            index_file = self._generate_master_index()
            generated_files.append(index_file)
            
            logger.info(f"Generated {len(generated_files)} multi-language type files")
            
        except Exception as e:
            logger.error(f"Failed to generate multi-language types: {str(e)}")
            raise
        
        return generated_files
    
    def _generate_for_language(self, language: str, analysis_results: Dict[str, Any]) -> List[Path]:
        """Generate type definitions for a specific language with all naming variants."""
        language_files = []
        
        # Create language directory
        language_dir = self.output_base_dir / language
        language_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate for each naming variant
        for interface_naming, property_naming in self.naming_variants:
            variant_files = self._generate_language_variant(
                language, interface_naming, property_naming, analysis_results
            )
            language_files.extend(variant_files)
        
        # Generate language index file
        language_index = self._generate_language_index(language)
        language_files.append(language_index)
        
        return language_files
    
    def _generate_language_variant(
        self, 
        language: str, 
        interface_naming: str, 
        property_naming: str, 
        analysis_results: Dict[str, Any]
    ) -> List[Path]:
        """Generate type definitions for a specific language and naming variant."""
        
        # Create naming variant directory
        variant_name = f"{interface_naming}_{property_naming}"
        variant_dir = self.output_base_dir / language / variant_name
        variant_dir.mkdir(parents=True, exist_ok=True)
        
        if language == "typescript":
            return self._generate_typescript_variant(
                variant_dir, interface_naming, property_naming, analysis_results
            )
        else:
            return self._generate_generic_language_variant(
                language, variant_dir, interface_naming, property_naming, analysis_results
            )
    
    def _generate_typescript_variant(
        self,
        output_dir: Path,
        interface_naming: str,
        property_naming: str,
        analysis_results: Dict[str, Any]
    ) -> List[Path]:
        """Generate TypeScript variant using the enhanced generator."""
        
        # Create temporary config for this variant
        temp_config = self.config.model_copy(deep=True)
        temp_config.output.typescript_output_dir = output_dir
        
        ts_config = TypeScriptGeneratorConfig(
            language=LanguageTemplate.TYPESCRIPT,
            interface_naming=NamingConvention(interface_naming),
            property_naming=NamingConvention(property_naming),
            preserve_django_names=self.preserve_django_names,
        )
        
        generator = EnhancedTypeScriptGenerator(temp_config, ts_config)
        return generator.generate_types_from_analysis(analysis_results)
    
    def _generate_generic_language_variant(
        self,
        language: str,
        output_dir: Path,
        interface_naming: str,
        property_naming: str,
        analysis_results: Dict[str, Any]
    ) -> List[Path]:
        """Generate variant for non-TypeScript languages using language templates."""
        
        generated_files = []
        
        try:
            # Convert analysis results to interface definitions
            app_interfaces = {}
            
            for app_name, app_data in analysis_results.items():
                if not app_data.get('serializers'):
                    continue
                
                interfaces = self._convert_serializers_to_interfaces(
                    app_data['serializers'], interface_naming, property_naming
                )
                app_interfaces[app_name] = interfaces
            
            # Generate files for each app
            language_template = LanguageTemplate(language)
            for app_name, interfaces in app_interfaces.items():
                if interfaces:
                    app_file = self._generate_app_language_file(
                        output_dir, app_name, interfaces, language_template
                    )
                    generated_files.append(app_file)
            
            # Generate language index
            if app_interfaces:
                index_file = self._generate_variant_index(output_dir, list(app_interfaces.keys()), language)
                generated_files.append(index_file)
            
        except Exception as e:
            logger.warning(f"Failed to generate {language} variant with {interface_naming}/{property_naming}: {str(e)}")
        
        return generated_files
    
    def _convert_serializers_to_interfaces(
        self, serializers: List[Any], interface_naming: str, property_naming: str
    ) -> List[InterfaceDefinition]:
        """Convert serializer data to interface definitions."""
        interfaces = []
        
        for serializer in serializers:
            try:
                if not hasattr(serializer, 'name'):
                    continue
                
                # Transform names according to conventions
                from ..utils.naming_conventions import NamingTransformer
                interface_name = getattr(NamingTransformer, f"to_{interface_naming}")(serializer.name)
                
                fields = []
                if hasattr(serializer, 'fields') and serializer.fields:
                    for field_name, field_info in serializer.fields.items():
                        # Transform property name
                        prop_name = getattr(NamingTransformer, f"to_{property_naming}")(field_name) \
                                    if not self.preserve_django_names else field_name
                        
                        # Map Django type to language type
                        field_type = getattr(field_info, 'type', 'any')
                        
                        field_def = FieldDefinition(
                            name=prop_name,
                            type_hint=self._map_django_type_to_language(field_type, LanguageTemplate(self.primary_language)),
                            is_optional=getattr(field_info, 'required', True) == False,
                            is_readonly=getattr(field_info, 'read_only', False),
                            is_nullable=getattr(field_info, 'allow_null', False),
                            description=getattr(field_info, 'help_text', None)
                        )
                        fields.append(field_def)
                
                interface = InterfaceDefinition(
                    name=interface_name,
                    fields=fields,
                    description=f"Generated from {serializer.name} serializer"
                )
                interfaces.append(interface)
                
            except Exception as e:
                serializer_name = getattr(serializer, 'name', 'unknown')
                logger.debug(f"Failed to convert serializer {serializer_name}: {str(e)}")
        
        return interfaces
    
    def _map_django_type_to_language(self, django_type: str, language: LanguageTemplate) -> str:
        """Map Django field type to language-specific type."""
        generator = create_language_generator(language)
        return generator.generate_type_mapping(django_type)
    
    def _generate_app_language_file(
        self, output_dir: Path, app_name: str, interfaces: List[InterfaceDefinition], language: LanguageTemplate
    ) -> Path:
        """Generate file for a specific app in a specific language."""
        
        # Determine file extension
        extensions = {
            LanguageTemplate.TYPESCRIPT: ".d.ts",
            LanguageTemplate.PYTHON: ".py", 
            LanguageTemplate.JAVA: ".java",
        }
        extension = extensions.get(language, ".txt")
        
        app_file = output_dir / f"{app_name}{extension}"
        
        # Generate content
        content = generate_models_for_language(
            interfaces, language, f"Generated types for {app_name} app"
        )
        
        app_file.write_text(content)
        logger.info(f"Generated {language.value} file: {app_file} ({len(interfaces)} interfaces)")
        
        return app_file
    
    def _generate_variant_index(self, output_dir: Path, app_names: List[str], language: str) -> Path:
        """Generate index file for a specific variant."""
        
        extensions = {"typescript": ".d.ts", "python": ".py", "java": ".java"}
        extension = extensions.get(language, ".txt")
        
        index_file = output_dir / f"index{extension}"
        
        lines = [
            f"/**",
            f" * {language.title()} API Types Index",
            f" * Generated for Django API v{self.config.version or '1.0.0'}",
            f" */",
            "",
        ]
        
        for app_name in sorted(app_names):
            if language == "typescript":
                lines.append(f"export * from './{app_name}';")
            elif language == "python":
                lines.append(f"from .{app_name} import *")
            else:
                lines.append(f"// {app_name} types")
        
        index_file.write_text("\\n".join(lines))
        return index_file
    
    def _generate_language_index(self, language: str) -> Path:
        """Generate index file for all variants of a language."""
        
        language_dir = self.output_base_dir / language
        index_file = language_dir / "README.md"
        
        content = f"""# {language.title()} API Types

This directory contains API type definitions for {language} in multiple naming conventions.

## Available Naming Variants:

"""
        
        for interface_naming, property_naming in self.naming_variants:
            variant_name = f"{interface_naming}_{property_naming}"
            content += f"- **{variant_name}**: Interfaces in {interface_naming}, properties in {property_naming}\\n"
        
        content += f"""
## Usage:

Choose the naming convention that matches your project's style:

```{language}
// For camelCase properties with PascalCase interfaces
import {{ UserProfile }} from './{self.naming_variants[0][0]}_{self.naming_variants[0][1]}/users';
```
"""
        
        index_file.write_text(content)
        return index_file
    
    def _generate_master_index(self) -> Path:
        """Generate master index file for all languages and variants."""
        
        index_file = self.output_base_dir / "README.md"
        
        content = f"""# Multi-Language API Types

Generated API type definitions for Django API v{self.config.version or '1.0.0'}

## Available Languages:

"""
        
        for language in self.languages:
            content += f"- **{language}**: See `{language}/` directory\\n"
        
        content += f"""
## Available Naming Conventions:

"""
        
        for interface_naming, property_naming in self.naming_variants:
            content += f"- **{interface_naming}_{property_naming}**: Interfaces in {interface_naming}, properties in {property_naming}\\n"
        
        content += """
## Directory Structure:

```
types_multi/
├── typescript/
│   ├── PascalCase_camelCase/
│   ├── snake_case_snake_case/
│   └── ...
├── python/
│   ├── PascalCase_snake_case/
│   └── ...
└── java/
    └── PascalCase_camelCase/
```

Choose the language and naming convention that matches your project's requirements.
"""
        
        index_file.write_text(content)
        return index_file