"""
AI prompt templates for Django code analysis
"""

from typing import Dict, Any


class PromptTemplates:
    """Collection of prompt templates for AI analysis"""
    
    SERIALIZER_ANALYSIS = """
Analyze the following Django REST Framework serializer code and provide detailed information about its fields, relationships, and validation logic.

Serializer Code:
```python
{serializer_code}
```

Context Information:
- App Name: {app_name}
- File Path: {file_path}
- Related Models: {related_models}

Please provide analysis in the following format:

## Field Analysis
For each field, determine:
- Actual data type (string, integer, boolean, etc.)
- Whether it's required or optional
- Default values if any
- Validation rules (max_length, min_value, etc.)
- Related model or nested serializer
- Purpose and description based on field name and context

## Relationships
Identify:
- Foreign key relationships
- Many-to-many relationships  
- Nested serializer relationships
- Reverse relationships

## Validation Logic
Analyze any custom validation methods:
- Field-level validation
- Object-level validation
- Cross-field validation rules

## API Documentation
Generate:
- Human-readable field descriptions
- Example request/response payloads
- Common use cases for this serializer

Focus on accuracy and provide specific technical details that would be useful for API documentation.
"""

    VIEW_ANALYSIS = """
Analyze the following Django REST Framework view/viewset code and provide comprehensive endpoint information.

View Code:
```python
{view_code}
```

Context Information:
- App Name: {app_name}
- File Path: {file_path}
- URL Patterns: {url_patterns}
- Related Serializers: {serializers}

Please provide analysis in the following format:

## Endpoint Mapping
For each HTTP method supported:
- Exact URL pattern
- HTTP method (GET, POST, PUT, PATCH, DELETE)
- Expected request format
- Response format
- Status codes returned

## Authentication & Permissions
Analyze:
- Authentication requirements
- Permission classes and their effects
- Who can access these endpoints

## Query Parameters
Identify supported query parameters:
- Filtering options
- Search capabilities
- Ordering/sorting options
- Pagination parameters

## Request/Response Examples
Generate realistic examples:
- Sample request payloads for POST/PUT/PATCH
- Expected response structures
- Error response formats

## Business Logic
Describe:
- What business operations this view performs
- Data validation and processing
- Side effects (emails, notifications, etc.)

Focus on creating clear, accurate API documentation that developers can use immediately.
"""

    TYPE_INFERENCE = """
Analyze the following Django model field or serializer field and infer the most appropriate TypeScript type.

Field Information:
- Field Name: {field_name}
- Field Type: {field_type}
- Field Options: {field_options}
- Context: {context}

Consider these factors:
1. Django/DRF field type mapping
2. Field constraints (max_length, choices, etc.)
3. Nullable/optional properties
4. Related models or nested structures

Provide the TypeScript type definition in this format:
```typescript
{field_name}: TypeDefinition;
```

If it's a complex type, provide the complete interface definition.
For choice fields, create appropriate union types.
For related fields, reference the appropriate interface.

Additional context about Django to TypeScript mappings:
- CharField → string
- IntegerField → number
- BooleanField → boolean
- DateField → string (ISO date)
- DateTimeField → string (ISO datetime)
- JSONField → object or specific interface
- ForeignKey → referenced interface
- ManyToMany → array of referenced interface

Be precise and consider all edge cases.
"""

    DOCUMENTATION_ENHANCEMENT = """
You are analyzing Django REST Framework code to generate high-quality API documentation. 

Code Context:
{code_context}

Analysis Results:
{analysis_results}

Please enhance this analysis to create professional API documentation:

## Improved Descriptions
Rewrite technical field names and descriptions to be user-friendly:
- Convert snake_case to readable phrases
- Explain business purpose, not just technical details
- Add context about when and why to use each field

## Error Handling
Document common errors:
- Required field validation errors
- Format validation errors
- Permission denied scenarios
- Not found cases

## Usage Examples
Create realistic, practical examples:
- Common request patterns
- Edge cases developers should know about
- Integration examples with frontend code

## Best Practices
Include recommendations:
- Optimal request formats
- Performance considerations
- Security best practices
- Rate limiting guidance

Make this documentation that a frontend developer could read and immediately understand how to integrate with the API.
"""

    RELATIONSHIP_MAPPING = """
Analyze the relationships between Django models, serializers, and views to create a comprehensive dependency map.

Components to analyze:
{components}

For each component, identify:

## Direct Dependencies
- Which models does this serializer reference?
- Which serializers does this view use?
- Which views use this serializer?

## Indirect Relationships
- Nested serializer chains
- Foreign key traversals
- Reverse relationship implications

## Data Flow
- How data moves from models through serializers to API responses
- Transformation points where data structure changes
- Validation chains and where data is validated

## Impact Analysis
- If this component changes, what else needs to be updated?
- Which endpoints would be affected by model changes?
- Circular dependencies to watch out for

Present the results as a structured dependency graph that can guide documentation organization and help developers understand the system architecture.
"""

    @classmethod
    def get_prompt(cls, template_name: str, **kwargs) -> str:
        """
        Get a formatted prompt template
        
        Args:
            template_name: Name of the template to use
            **kwargs: Variables to substitute in the template
            
        Returns:
            Formatted prompt string
        """
        template = getattr(cls, template_name, None)
        if not template:
            raise ValueError(f"Unknown template: {template_name}")
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")
    
    @classmethod
    def list_templates(cls) -> list[str]:
        """List all available template names"""
        templates = []
        for attr_name in dir(cls):
            if not attr_name.startswith('_') and attr_name.isupper():
                templates.append(attr_name)
        return templates