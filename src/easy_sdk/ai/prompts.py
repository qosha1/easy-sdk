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

    API_STRUCTURE_ANALYSIS = """
Analyze the overall Django REST API structure and identify patterns for SDK generation.

API Structure Data:
- Total Apps: {total_apps}
- App Names: {app_names}
- Structure Details: {structure_data}

Please analyze and provide insights in JSON format:

```json
{{
  "common_patterns": [
    "List of common API patterns found (CRUD, nested resources, etc.)"
  ],
  "auth_strategy": "token|session|oauth|jwt|basic",
  "base_url_pattern": "/api/v1 or similar base pattern",
  "error_handling": {{
    "standard_format": "How errors are typically formatted",
    "common_codes": [400, 401, 403, 404, 500],
    "custom_error_fields": ["field_name"]
  }},
  "pagination_strategy": "page_number|offset_limit|cursor|none",
  "pagination_params": {{
    "page_param": "page",
    "size_param": "page_size",
    "default_size": 20
  }},
  "naming_conventions": {{
    "url_style": "snake_case|kebab-case|camelCase",
    "field_style": "snake_case|camelCase",
    "endpoint_patterns": ["common patterns like /api/app/resource/"]
  }},
  "data_patterns": {{
    "timestamp_format": "ISO 8601 or other format",
    "id_field_type": "integer|uuid|string",
    "common_field_names": ["id", "created_at", "updated_at"]
  }},
  "filtering_and_search": {{
    "supports_filtering": true,
    "filter_params": ["common filter parameter names"],
    "supports_search": true,
    "search_params": ["q", "search"]
  }},
  "sdk_generation_insights": {{
    "complexity_level": "simple|moderate|complex",
    "recommended_client_structure": "single|multi_app|service_based",
    "async_operations": ["endpoints that should be async"],
    "bulk_operations": ["endpoints that support bulk operations"],
    "file_upload_patterns": ["endpoints that handle file uploads"],
    "websocket_endpoints": ["real-time endpoints if any"]
  }}
}}
```

Focus on identifying patterns that will help generate clean, efficient SDK code. Look for:

1. **Consistency patterns** - How similar endpoints are structured
2. **Authentication flows** - How authentication is handled across the API
3. **Error patterns** - Consistent error response formats
4. **Data relationships** - How different resources relate to each other
5. **Operation patterns** - CRUD operations, bulk operations, nested resources
6. **Performance considerations** - Pagination, filtering, caching headers

Provide specific, actionable insights that an SDK generator can use to create high-quality client libraries.
"""

    MODEL_ANALYSIS = """
Analyze the following Django model code and provide comprehensive information about its structure, purpose, and field relationships.

Model Code:
```python
{model_code}
```

Context Information:
- App Name: {app_name}
- Model Name: {model_name}
- File Path: {file_path}
- Model Fields: {fields}
- Related Models: {relationships}

Please provide analysis in the following format:

## Business Purpose
Describe what this model represents in the business domain:
- What real-world entity or concept does this model represent?
- How does it fit into the overall application architecture?
- What business processes or workflows does it support?

## Field Analysis
For each field, provide:
- Business purpose and meaning
- Why specific validation rules are needed
- Examples of typical values
- How it relates to user workflows
- API documentation description that's user-friendly

## Relationships Analysis
Analyze model relationships:
- Foreign key relationships and their business meaning
- Many-to-many relationships and why they exist
- One-to-one relationships and their purpose
- How these relationships support business processes

## Usage Patterns
Identify common usage patterns:
- How is this model typically created?
- What are common query patterns?
- How does it integrate with other models?
- What are typical lifecycle states?

## API Integration
Consider how this model appears in APIs:
- What fields should be exposed in list vs detail views?
- What fields are safe for public API exposure?
- What computed properties might be useful?
- How should this model be represented in different API contexts?

Focus on providing insights that help generate better API documentation and understand the business context.
"""

    COMPONENT_RELATIONSHIP_ANALYSIS = """
Analyze the relationships between Django models, serializers, and views in this app to understand the data flow and API structure.

App Name: {app_name}

Models: {models}
Serializers: {serializers}
Views: {views}

Component Data:
{component_data}

Please analyze and provide insights in the following format:

## Data Flow Analysis
Map how data flows through the application:
- From models through serializers to API responses
- How user input flows from API requests through serializers to models
- Where data transformation happens
- What validation occurs at each stage

## Component Dependencies
Identify dependencies between components:
- Which serializers use which models?
- Which views use which serializers?
- What nested relationships exist?
- Where are circular dependencies or complex relationships?

## API Endpoint Mapping
For each view, identify:
- What serializers it uses for input vs output
- What models it operates on
- What business operations it performs
- How it fits into the overall API structure

## Consistency Analysis
Analyze consistency across components:
- Are naming conventions consistent?
- Are similar patterns used across different endpoints?
- Are there opportunities for consolidation or standardization?
- What patterns could be documented as best practices?

## Integration Points
Identify how components integrate:
- Where do different apps interact?
- What shared models or serializers exist?
- How do foreign key relationships affect API design?
- What cross-cutting concerns exist (permissions, filtering, etc.)?

Focus on insights that help understand the overall API architecture and improve documentation generation.
"""

    API_INSIGHTS_GENERATION = """
Analyze the overall Django REST API structure and generate comprehensive insights and recommendations.

API Statistics:
- Total Models: {total_models}
- Total Serializers: {total_serializers}
- Total Views: {total_views}
- Total Endpoints: {total_endpoints}
- Apps: {apps}

API Structure:
{api_structure}

Please provide comprehensive analysis in JSON format:

```json
{{
  "complexity_assessment": "simple|moderate|complex",
  "architectural_patterns": [
    "List of architectural patterns identified (REST, CRUD, nested resources, etc.)"
  ],
  "api_maturity_level": {{
    "level": "basic|intermediate|advanced",
    "reasoning": "Why this maturity level was assigned",
    "improvements_needed": ["List of areas for improvement"]
  }},
  "consistency_analysis": {{
    "naming_conventions": {{
      "consistent": true,
      "issues": ["Any naming inconsistencies found"],
      "recommendations": ["Suggestions for improvement"]
    }},
    "endpoint_patterns": {{
      "consistent": true,
      "common_patterns": ["List of common URL/endpoint patterns"],
      "exceptions": ["Any endpoints that don't follow patterns"]
    }},
    "response_formats": {{
      "consistent": true,
      "standard_format": "Description of standard response format",
      "variations": ["Any response format variations"]
    }}
  }},
  "security_analysis": {{
    "authentication_strategy": "token|session|jwt|oauth|mixed",
    "permission_patterns": ["Common permission patterns used"],
    "security_recommendations": [
      "Specific security improvements needed"
    ]
  }},
  "performance_considerations": {{
    "potential_n_plus_1_queries": ["Endpoints that might have N+1 query issues"],
    "pagination_strategy": "Description of pagination approach",
    "caching_opportunities": ["Where caching could be beneficial"],
    "optimization_recommendations": ["Performance improvement suggestions"]
  }},
  "documentation_recommendations": {{
    "priority_endpoints": ["Most important endpoints to document first"],
    "complex_workflows": ["Multi-step processes that need workflow documentation"],
    "example_scenarios": ["Real-world use cases to include in docs"],
    "integration_guides": ["Types of integration guides needed"]
  }},
  "sdk_generation_insights": {{
    "client_architecture": "single|multi_service|modular",
    "async_requirements": ["Endpoints that should be async in SDKs"],
    "error_handling_patterns": ["Common error patterns to handle"],
    "retry_strategies": ["Endpoints that need retry logic"],
    "rate_limiting_considerations": ["Rate limiting patterns to implement"],
    "authentication_flows": ["Auth flows to implement in SDKs"]
  }},
  "api_evolution_recommendations": {{
    "versioning_strategy": "Recommended API versioning approach",
    "breaking_change_risks": ["Areas where breaking changes might occur"],
    "extensibility_patterns": ["How the API can be extended safely"],
    "deprecation_strategy": ["How to handle deprecated endpoints"]
  }},
  "business_domain_insights": {{
    "core_entities": ["Main business entities in the API"],
    "business_workflows": ["Key business processes supported"],
    "user_personas": ["Types of API consumers"],
    "integration_scenarios": ["Common integration patterns"]
  }}
}}
```

Focus on actionable insights that help with:
1. Generating high-quality API documentation
2. Creating robust SDKs and client libraries
3. Improving API design and consistency
4. Planning future API evolution
5. Understanding business context and user needs
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