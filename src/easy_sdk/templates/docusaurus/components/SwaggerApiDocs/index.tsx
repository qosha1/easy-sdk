import React from 'react';
import ApiExplorer from '../ApiExplorer';
import { EndpointConverter, DjangoSerializer, DjangoEndpoint } from '../ApiExplorer/endpointConverter';

interface SwaggerApiDocsProps {
  appName: string;
  title?: string;
  description?: string;
  serializers?: DjangoSerializer[];
  endpoints?: DjangoEndpoint[];
  serverUrl?: string;
}

const SwaggerApiDocs: React.FC<SwaggerApiDocsProps> = ({
  appName,
  title,
  description,
  serializers = [],
  endpoints = [],
  serverUrl = 'http://localhost:8000'
}) => {
  // Convert Django endpoints to Swagger format
  const converter = new EndpointConverter(serializers);
  const swaggerEndpoints = converter.convertEndpoints(endpoints, appName);

  return (
    <div>
      {description && (
        <div style={{ 
          padding: '20px 24px', 
          background: 'white', 
          borderBottom: '1px solid #e8e8e8',
          marginBottom: '0'
        }}>
          <p style={{ 
            margin: 0, 
            color: '#666', 
            fontSize: '16px', 
            lineHeight: '1.6' 
          }}>
            {description}
          </p>
        </div>
      )}
      
      <ApiExplorer
        appName={appName}
        endpoints={swaggerEndpoints}
        serverUrl={serverUrl}
        title={title}
      />
    </div>
  );
};

export default SwaggerApiDocs;