// Generate Swagger-like markdown from Django analysis data

import { DjangoSerializer, DjangoEndpoint, EndpointConverter } from '../ApiExplorer/endpointConverter';

interface AppAnalysisData {
  serializers: any[];
  views: any[];
  app_info: any;
}

export function generateSwaggerMarkdown(
  appName: string, 
  analysisData: AppAnalysisData,
  title?: string
): string {
  // Convert Django analysis data to component format
  const serializers = convertSerializersToComponentFormat(analysisData.serializers);
  const endpoints = convertViewsToEndpoints(analysisData.views);
  
  const componentSerializers = JSON.stringify(serializers, null, 2);
  const componentEndpoints = JSON.stringify(endpoints, null, 2);
  
  const description = generateAppDescription(appName, analysisData);
  
  return `---
sidebar_position: ${getSidebarPosition(appName)}
---

# ${title || `${appName.charAt(0).toUpperCase() + appName.slice(1)} API`}

import SwaggerApiDocs from '@site/src/components/SwaggerApiDocs';

<SwaggerApiDocs 
  appName="${appName}"
  title="${title || `${appName.charAt(0).toUpperCase() + appName.slice(1)} API`}"
  description="${description}"
  serializers={${componentSerializers}}
  endpoints={${componentEndpoints}}
/>

## Quick Examples

${generateQuickExamples(endpoints, serializers)}

## Legacy Documentation

import DynamicTypeLoader from '@site/src/components/DynamicTypeLoader';

<DynamicTypeLoader 
  appName="${appName}"
  title="${appName.charAt(0).toUpperCase() + appName.slice(1)} App Data Models"
  showAllVariants={false}
/>`;
}

function convertSerializersToComponentFormat(serializers: any[]): DjangoSerializer[] {
  return serializers.map(serializer => ({
    name: serializer.name || 'UnknownSerializer',
    fields: convertFieldsToComponentFormat(serializer.fields || {}),
    docstring: serializer.docstring || `${serializer.name} data structure`
  }));
}

function convertFieldsToComponentFormat(fields: any): { [key: string]: any } {
  const convertedFields: { [key: string]: any } = {};
  
  Object.entries(fields).forEach(([fieldName, fieldInfo]: [string, any]) => {
    convertedFields[fieldName] = {
      type: fieldInfo.type || 'CharField',
      required: fieldInfo.required !== false,
      read_only: fieldInfo.read_only || false,
      write_only: fieldInfo.write_only || false,
      allow_null: fieldInfo.allow_null || false,
      help_text: fieldInfo.help_text || `${fieldName} field`,
      max_length: fieldInfo.max_length,
      choices: fieldInfo.choices,
      default: fieldInfo.default
    };
  });
  
  return convertedFields;
}

function convertViewsToEndpoints(views: any[]): DjangoEndpoint[] {
  const endpoints: DjangoEndpoint[] = [];
  
  views.forEach(view => {
    if (view.endpoints && Array.isArray(view.endpoints)) {
      view.endpoints.forEach((endpoint: any) => {
        endpoints.push({
          method: endpoint.method || 'GET',
          path: endpoint.path || '/',
          description: endpoint.description || `${endpoint.method} endpoint`,
          serializer_class: endpoint.serializer_class || view.serializer_class,
          tags: endpoint.tags || [generateTagFromPath(endpoint.path)],
          name: endpoint.name,
          permission_classes: view.permission_classes,
          authentication_classes: view.authentication_classes
        });
      });
    }
  });
  
  return endpoints;
}

function generateTagFromPath(path: string): string {
  const segments = path.split('/').filter(Boolean);
  
  // Find the main resource (usually the first non-api segment)
  for (const segment of segments) {
    if (segment !== 'api' && segment !== 'v1' && !segment.includes('{')) {
      return segment.charAt(0).toUpperCase() + segment.slice(1).replace('-', ' ');
    }
  }
  
  return 'API';
}

function generateAppDescription(appName: string, analysisData: AppAnalysisData): string {
  const baseDescriptions: { [key: string]: string } = {
    'users': 'The Users API provides endpoints for user management, authentication, profiles, addresses, and wishlists. This includes login/registration, user profiles, shipping/billing addresses, and wishlist functionality.',
    'products': 'The Products API provides endpoints for managing product catalogs, categories, brands, and product images in the e-commerce system. This includes hierarchical product categorization, brand management, product catalog with pricing and inventory, and image management.',
    'orders': 'The Orders API provides endpoints for managing shopping carts, orders, and payments in the e-commerce system. This includes cart management for authenticated and anonymous users, order processing and management, payment processing and tracking, and individual order items.',
    'reviews': 'The Reviews API provides endpoints for managing product reviews, ratings, and customer feedback. This includes review creation, moderation, ratings, and customer feedback management.'
  };
  
  return baseDescriptions[appName] || `The ${appName.charAt(0).toUpperCase() + appName.slice(1)} API provides endpoints for ${appName} management and operations.`;
}

function getSidebarPosition(appName: string): number {
  const positions: { [key: string]: number } = {
    'products': 1,
    'users': 2,
    'orders': 3,
    'reviews': 4
  };
  
  return positions[appName] || 5;
}

function generateQuickExamples(endpoints: DjangoEndpoint[], serializers: DjangoSerializer[]): string {
  let examples = '';
  
  // Find a POST endpoint for create example
  const createEndpoint = endpoints.find(ep => 
    ep.method.toUpperCase() === 'POST' && 
    !ep.path.includes('{') &&
    ep.serializer_class
  );
  
  if (createEndpoint) {
    const serializer = serializers.find(s => s.name === createEndpoint.serializer_class);
    if (serializer) {
      const exampleData = generateExampleData(serializer);
      
      examples += `### ${createEndpoint.description || 'Create Resource'}

\`\`\`bash
${createEndpoint.method.toUpperCase()} ${createEndpoint.path}
Authorization: Bearer your-token-here
Content-Type: application/json

${JSON.stringify(exampleData, null, 2)}
\`\`\`

`;
    }
  }
  
  // Find a GET endpoint for list/search example
  const listEndpoint = endpoints.find(ep => 
    ep.method.toUpperCase() === 'GET' && 
    !ep.path.includes('{') &&
    (ep.path.includes('search') || ep.description.toLowerCase().includes('list'))
  );
  
  if (listEndpoint) {
    examples += `### ${listEndpoint.description || 'List Resources'}

\`\`\`bash
${listEndpoint.method.toUpperCase()} ${listEndpoint.path}
Authorization: Bearer your-token-here
\`\`\`

`;
  }
  
  return examples || '### Example Usage\n\nSee the interactive API explorer above to test endpoints.\n\n';
}

function generateExampleData(serializer: DjangoSerializer): any {
  const exampleData: any = {};
  
  Object.entries(serializer.fields).forEach(([fieldName, field]) => {
    if (!field.read_only) {
      exampleData[fieldName] = generateFieldExample(field, fieldName);
    }
  });
  
  return exampleData;
}

function generateFieldExample(field: any, fieldName: string): any {
  if (field.choices && field.choices.length > 0) {
    return Array.isArray(field.choices[0]) ? field.choices[0][0] : field.choices[0];
  }
  
  if (field.default !== undefined) {
    return field.default;
  }
  
  // Generate based on field type
  switch (field.type) {
    case 'EmailField':
      return 'user@example.com';
    case 'URLField':
      return 'https://example.com';
    case 'IntegerField':
    case 'PositiveIntegerField':
      return fieldName.includes('id') ? 1 : 123;
    case 'DecimalField':
      return fieldName.includes('price') ? "99.99" : "123.45";
    case 'BooleanField':
      return fieldName.includes('is_') ? true : false;
    case 'DateTimeField':
      return new Date().toISOString();
    case 'DateField':
      return new Date().toISOString().split('T')[0];
    case 'TextField':
      return `Sample ${fieldName.replace('_', ' ')} content`;
    case 'CharField':
      if (fieldName.includes('name')) return `Sample ${fieldName}`;
      if (fieldName.includes('email')) return 'user@example.com';
      if (fieldName.includes('phone')) return '+1-555-0123';
      return `Sample ${fieldName}`;
    case 'JSONField':
      return {};
    case 'ForeignKey':
      return 1;
    case 'ManyToManyField':
      return [1, 2];
    default:
      return `Sample ${fieldName}`;
  }
}

export default generateSwaggerMarkdown;