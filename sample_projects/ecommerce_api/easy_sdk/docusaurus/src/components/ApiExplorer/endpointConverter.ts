// Endpoint Converter - Transform Django analysis to Swagger-like format

export interface DjangoEndpoint {
  method: string;
  path: string;
  name?: string;
  description?: string;
  serializer_class?: string;
  permission_classes?: string[];
  authentication_classes?: string[];
}

export interface DjangoSerializer {
  name: string;
  fields: { [key: string]: DjangoField };
  file_path?: string;
  docstring?: string;
}

export interface DjangoField {
  type: string;
  required?: boolean;
  allow_null?: boolean;
  read_only?: boolean;
  write_only?: boolean;
  help_text?: string;
  choices?: any[];
  max_length?: number;
  default?: any;
}

export interface SwaggerEndpoint {
  method: string;
  path: string;
  description: string;
  summary?: string;
  parameters?: SwaggerParameter[];
  requestBody?: SwaggerSchema;
  responses: { [key: string]: SwaggerResponse };
  tags: string[];
  operationId: string;
}

export interface SwaggerParameter {
  name: string;
  in: 'path' | 'query' | 'header' | 'body';
  description?: string;
  required: boolean;
  schema: SwaggerSchema;
}

export interface SwaggerSchema {
  type: string;
  properties?: { [key: string]: SwaggerSchema };
  items?: SwaggerSchema;
  example?: any;
  description?: string;
  required?: string[];
  enum?: any[];
  format?: string;
  maxLength?: number;
  nullable?: boolean;
}

export interface SwaggerResponse {
  description: string;
  schema?: SwaggerSchema;
  examples?: { [key: string]: any };
}

export class EndpointConverter {
  private serializers: Map<string, DjangoSerializer> = new Map();

  constructor(serializers: DjangoSerializer[]) {
    serializers.forEach(s => this.serializers.set(s.name, s));
  }

  convertEndpoints(djangoEndpoints: DjangoEndpoint[], appName: string): SwaggerEndpoint[] {
    return djangoEndpoints.map(endpoint => this.convertEndpoint(endpoint, appName));
  }

  private convertEndpoint(endpoint: DjangoEndpoint, appName: string): SwaggerEndpoint {
    const method = endpoint.method.toLowerCase();
    const path = this.convertPath(endpoint.path);
    
    // Generate tags from app name and path
    const tags = [appName];
    
    // Get serializer info
    const serializerName = endpoint.serializer_class;
    const serializer = serializerName ? this.serializers.get(serializerName) : null;

    // Generate operation ID
    const operationId = this.generateOperationId(method, path, appName);

    // Generate parameters
    const parameters = this.extractParameters(path, method, serializer);

    // Generate request body for POST/PUT/PATCH
    const requestBody = this.generateRequestBody(method, serializer);

    // Generate responses
    const responses = this.generateResponses(method, serializer);

    // Generate summary and description
    const { summary, description } = this.generateSummaryAndDescription(
      endpoint, method, path, appName
    );

    return {
      method: method.toUpperCase(),
      path,
      description,
      summary,
      parameters,
      requestBody,
      responses,
      tags,
      operationId
    };
  }

  private convertPath(djangoPath: string): string {
    // Convert Django path format to OpenAPI format
    // Example: /api/users/<int:id>/ -> /api/users/{id}
    return djangoPath
      .replace(/<(\w+:)?(\w+)>/g, '{$2}')
      .replace(/\/$/, '') || '/';
  }

  private generateOperationId(method: string, path: string, appName: string): string {
    // Generate a unique operation ID
    const pathSegments = path.split('/').filter(Boolean);
    const resource = pathSegments[pathSegments.length - 1] || appName;
    const action = this.getActionFromMethod(method);
    
    return `${action}${this.capitalize(resource)}`;
  }

  private getActionFromMethod(method: string): string {
    const actions = {
      'get': 'get',
      'post': 'create',
      'put': 'update',
      'patch': 'update',
      'delete': 'delete'
    };
    return actions[method.toLowerCase()] || method.toLowerCase();
  }

  private extractParameters(path: string, method: string, serializer?: DjangoSerializer): SwaggerParameter[] {
    const parameters: SwaggerParameter[] = [];

    // Extract path parameters
    const pathParams = path.match(/\{(\w+)\}/g);
    if (pathParams) {
      pathParams.forEach(param => {
        const paramName = param.slice(1, -1); // Remove { }
        parameters.push({
          name: paramName,
          in: 'path',
          required: true,
          description: `${this.capitalize(paramName)} identifier`,
          schema: { type: 'string' }
        });
      });
    }

    // Add common query parameters for GET requests
    if (method.toLowerCase() === 'get') {
      parameters.push(
        {
          name: 'page',
          in: 'query',
          required: false,
          description: 'Page number for pagination',
          schema: { type: 'integer', example: 1 }
        },
        {
          name: 'page_size',
          in: 'query',
          required: false,
          description: 'Number of items per page',
          schema: { type: 'integer', example: 20 }
        }
      );
    }

    // Add authorization header
    parameters.push({
      name: 'Authorization',
      in: 'header',
      required: false,
      description: 'Bearer token for authentication',
      schema: { type: 'string', example: 'Bearer your-token-here' }
    });

    return parameters;
  }

  private generateRequestBody(method: string, serializer?: DjangoSerializer): SwaggerSchema | undefined {
    if (!['post', 'put', 'patch'].includes(method.toLowerCase()) || !serializer) {
      return undefined;
    }

    const schema = this.convertSerializer(serializer);
    
    // For PATCH, make all fields optional
    if (method.toLowerCase() === 'patch' && schema.properties) {
      schema.required = [];
      Object.keys(schema.properties).forEach(key => {
        if (schema.properties![key]) {
          schema.properties![key].nullable = true;
        }
      });
    }

    return schema;
  }

  private generateResponses(method: string, serializer?: DjangoSerializer): { [key: string]: SwaggerResponse } {
    const responses: { [key: string]: SwaggerResponse } = {};

    // Success responses
    switch (method.toLowerCase()) {
      case 'get':
        if (serializer) {
          responses['200'] = {
            description: 'Successful response',
            schema: this.convertSerializer(serializer),
            examples: {
              'application/json': this.generateExample(serializer)
            }
          };
        } else {
          responses['200'] = {
            description: 'Successful response',
            schema: { type: 'object' }
          };
        }
        break;

      case 'post':
        if (serializer) {
          responses['201'] = {
            description: 'Resource created successfully',
            schema: this.convertSerializer(serializer),
            examples: {
              'application/json': this.generateExample(serializer)
            }
          };
        }
        break;

      case 'put':
      case 'patch':
        if (serializer) {
          responses['200'] = {
            description: 'Resource updated successfully',
            schema: this.convertSerializer(serializer),
            examples: {
              'application/json': this.generateExample(serializer)
            }
          };
        }
        break;

      case 'delete':
        responses['204'] = {
          description: 'Resource deleted successfully'
        };
        break;
    }

    // Common error responses
    responses['400'] = {
      description: 'Bad Request - Invalid input data',
      schema: {
        type: 'object',
        properties: {
          error: { type: 'string' },
          details: { type: 'object' }
        }
      }
    };

    responses['401'] = {
      description: 'Unauthorized - Authentication required',
      schema: {
        type: 'object',
        properties: {
          detail: { type: 'string', example: 'Authentication credentials were not provided.' }
        }
      }
    };

    responses['404'] = {
      description: 'Not Found - Resource does not exist',
      schema: {
        type: 'object',
        properties: {
          detail: { type: 'string', example: 'Not found.' }
        }
      }
    };

    return responses;
  }

  private convertSerializer(serializer: DjangoSerializer): SwaggerSchema {
    const properties: { [key: string]: SwaggerSchema } = {};
    const required: string[] = [];

    Object.entries(serializer.fields).forEach(([fieldName, field]) => {
      properties[fieldName] = this.convertField(field);
      
      if (field.required && !field.read_only) {
        required.push(fieldName);
      }
    });

    return {
      type: 'object',
      properties,
      required,
      description: serializer.docstring || `${serializer.name} data structure`,
      example: this.generateExample(serializer)
    };
  }

  private convertField(field: DjangoField): SwaggerSchema {
    const schema: SwaggerSchema = {
      type: this.mapDjangoTypeToSwagger(field.type),
      description: field.help_text,
      nullable: field.allow_null
    };

    // Handle choices as enums
    if (field.choices) {
      schema.enum = field.choices.map(choice => 
        Array.isArray(choice) ? choice[0] : choice
      );
    }

    // Add format and constraints
    if (field.max_length) {
      schema.maxLength = field.max_length;
    }

    // Add examples based on field type and name
    schema.example = this.generateFieldExample(field, schema.type);

    return schema;
  }

  private mapDjangoTypeToSwagger(djangoType: string): string {
    const typeMapping: { [key: string]: string } = {
      'CharField': 'string',
      'TextField': 'string',
      'EmailField': 'string',
      'URLField': 'string',
      'SlugField': 'string',
      'UUIDField': 'string',
      'IntegerField': 'integer',
      'BigIntegerField': 'integer',
      'SmallIntegerField': 'integer',
      'PositiveIntegerField': 'integer',
      'FloatField': 'number',
      'DecimalField': 'number',
      'BooleanField': 'boolean',
      'DateTimeField': 'string',
      'DateField': 'string',
      'TimeField': 'string',
      'JSONField': 'object',
      'FileField': 'string',
      'ImageField': 'string',
      'ForeignKey': 'integer',
      'OneToOneField': 'integer',
      'ManyToManyField': 'array'
    };

    return typeMapping[djangoType] || 'string';
  }

  private generateFieldExample(field: DjangoField, swaggerType: string): any {
    if (field.default !== undefined) {
      return field.default;
    }

    if (field.choices && field.choices.length > 0) {
      return Array.isArray(field.choices[0]) ? field.choices[0][0] : field.choices[0];
    }

    // Generate examples based on type
    switch (swaggerType) {
      case 'string':
        if (field.type === 'EmailField') return 'user@example.com';
        if (field.type === 'URLField') return 'https://example.com';
        if (field.type === 'UUIDField') return '123e4567-e89b-12d3-a456-426614174000';
        return 'string';
      case 'integer':
        return 123;
      case 'number':
        return 123.45;
      case 'boolean':
        return true;
      case 'array':
        return [];
      case 'object':
        return {};
      default:
        return null;
    }
  }

  private generateExample(serializer: DjangoSerializer): any {
    const example: any = {};
    
    Object.entries(serializer.fields).forEach(([fieldName, field]) => {
      if (!field.write_only) {
        example[fieldName] = this.generateFieldExample(field, this.mapDjangoTypeToSwagger(field.type));
      }
    });

    return example;
  }

  private generateSummaryAndDescription(
    endpoint: DjangoEndpoint, 
    method: string, 
    path: string, 
    appName: string
  ): { summary: string; description: string } {
    const action = this.getActionFromMethod(method);
    const resource = this.extractResourceFromPath(path);
    
    const summary = endpoint.name || 
      `${this.capitalize(action)} ${resource || appName}`;
    
    const description = endpoint.description || 
      `${this.capitalize(action)} operation for ${resource || appName} resource.`;

    return { summary, description };
  }

  private extractResourceFromPath(path: string): string {
    const segments = path.split('/').filter(Boolean);
    // Find the last non-parameter segment
    for (let i = segments.length - 1; i >= 0; i--) {
      if (!segments[i].includes('{')) {
        return segments[i];
      }
    }
    return '';
  }

  private capitalize(str: string): string {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }
}

export default EndpointConverter;