import React, { useState, useEffect } from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';

interface Endpoint {
  method: string;
  path: string;
  description: string;
  summary?: string;
  parameters?: Parameter[];
  requestBody?: Schema;
  responses?: { [key: string]: Response };
  tags?: string[];
}

interface Parameter {
  name: string;
  in: 'path' | 'query' | 'header' | 'body';
  description?: string;
  required?: boolean;
  schema: Schema;
}

interface Schema {
  type: string;
  properties?: { [key: string]: Schema };
  items?: Schema;
  example?: any;
  description?: string;
  required?: string[];
}

interface Response {
  description: string;
  schema?: Schema;
  examples?: { [key: string]: any };
}

interface ApiExplorerProps {
  appName: string;
  endpoints: Endpoint[];
  serverUrl?: string;
  title?: string;
}

const ApiExplorer: React.FC<ApiExplorerProps> = ({ 
  appName, 
  endpoints, 
  serverUrl = 'http://localhost:8000',
  title 
}) => {
  const [selectedServer, setSelectedServer] = useState(serverUrl);
  const [expandedEndpoints, setExpandedEndpoints] = useState<Set<string>>(new Set());
  const [activeEndpoint, setActiveEndpoint] = useState<string | null>(null);

  // Group endpoints by tags
  const groupedEndpoints = endpoints.reduce((groups, endpoint) => {
    const tag = endpoint.tags?.[0] || 'default';
    if (!groups[tag]) {
      groups[tag] = [];
    }
    groups[tag].push(endpoint);
    return groups;
  }, {} as { [key: string]: Endpoint[] });

  const getMethodColor = (method: string) => {
    switch (method.toUpperCase()) {
      case 'GET': return styles.methodGet;
      case 'POST': return styles.methodPost;
      case 'PUT': return styles.methodPut;
      case 'PATCH': return styles.methodPatch;
      case 'DELETE': return styles.methodDelete;
      default: return styles.methodDefault;
    }
  };

  const toggleEndpoint = (endpointId: string) => {
    const newExpanded = new Set(expandedEndpoints);
    if (newExpanded.has(endpointId)) {
      newExpanded.delete(endpointId);
    } else {
      newExpanded.add(endpointId);
    }
    setExpandedEndpoints(newExpanded);
  };

  return (
    <div className={styles.apiExplorer}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.titleSection}>
          <h1 className={styles.title}>
            {title || `${appName} API`}
            <span className={styles.version}>1.0.0</span>
            <span className={styles.spec}>OAS 3.0</span>
          </h1>
          <p className={styles.description}>
            Documentation of API endpoints for {appName}.
          </p>
        </div>

        {/* Server Selection */}
        <div className={styles.serverSection}>
          <label className={styles.serverLabel}>Servers</label>
          <select 
            className={styles.serverSelect}
            value={selectedServer}
            onChange={(e) => setSelectedServer(e.target.value)}
          >
            <option value="http://localhost:8000">http://localhost:8000</option>
            <option value="http://127.0.0.1:8000">http://127.0.0.1:8000</option>
            <option value="https://api.yourapp.com">https://api.yourapp.com</option>
          </select>
          <button className={styles.authorizeBtn}>
            🔒 Authorize
          </button>
        </div>
      </div>

      {/* API Groups */}
      <div className={styles.apiGroups}>
        {Object.entries(groupedEndpoints).map(([groupName, groupEndpoints]) => (
          <div key={groupName} className={styles.apiGroup}>
            <div className={styles.groupHeader}>
              <h2 className={styles.groupTitle}>{groupName}</h2>
              <button 
                className={styles.groupToggle}
                onClick={() => {
                  // Toggle all endpoints in this group
                  const groupEndpointIds = groupEndpoints.map(ep => `${ep.method}-${ep.path}`);
                  const newExpanded = new Set(expandedEndpoints);
                  const allExpanded = groupEndpointIds.every(id => newExpanded.has(id));
                  
                  if (allExpanded) {
                    groupEndpointIds.forEach(id => newExpanded.delete(id));
                  } else {
                    groupEndpointIds.forEach(id => newExpanded.add(id));
                  }
                  setExpandedEndpoints(newExpanded);
                }}
              >
                ▼
              </button>
            </div>

            {groupEndpoints.map((endpoint) => {
              const endpointId = `${endpoint.method}-${endpoint.path}`;
              const isExpanded = expandedEndpoints.has(endpointId);

              return (
                <div key={endpointId} className={styles.endpointCard}>
                  <div 
                    className={styles.endpointHeader}
                    onClick={() => toggleEndpoint(endpointId)}
                  >
                    <div className={styles.endpointInfo}>
                      <span className={clsx(styles.methodBadge, getMethodColor(endpoint.method))}>
                        {endpoint.method.toUpperCase()}
                      </span>
                      <span className={styles.endpointPath}>
                        {endpoint.path}
                      </span>
                      <span className={styles.endpointSummary}>
                        {endpoint.summary || endpoint.description}
                      </span>
                    </div>
                    <div className={styles.endpointActions}>
                      <button className={styles.lockIcon}>🔒</button>
                      <button className={styles.expandIcon}>
                        {isExpanded ? '▲' : '▼'}
                      </button>
                    </div>
                  </div>

                  {isExpanded && (
                    <EndpointDetails 
                      endpoint={endpoint}
                      serverUrl={selectedServer}
                    />
                  )}
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
};

// Separate component for endpoint details
const EndpointDetails: React.FC<{ endpoint: Endpoint; serverUrl: string }> = ({ 
  endpoint, 
  serverUrl 
}) => {
  const [activeTab, setActiveTab] = useState<'try' | 'schema'>('try');
  const [requestData, setRequestData] = useState<{ [key: string]: any }>({});
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const executeRequest = async () => {
    setLoading(true);
    try {
      // Build request URL
      let url = `${serverUrl}${endpoint.path}`;
      
      // Replace path parameters
      endpoint.parameters?.forEach(param => {
        if (param.in === 'path' && requestData[param.name]) {
          url = url.replace(`{${param.name}}`, requestData[param.name]);
        }
      });

      // Add query parameters
      const queryParams = new URLSearchParams();
      endpoint.parameters?.forEach(param => {
        if (param.in === 'query' && requestData[param.name]) {
          queryParams.append(param.name, requestData[param.name]);
        }
      });
      
      if (queryParams.toString()) {
        url += `?${queryParams.toString()}`;
      }

      const options: RequestInit = {
        method: endpoint.method,
        headers: {
          'Content-Type': 'application/json',
          ...Object.fromEntries(
            endpoint.parameters
              ?.filter(p => p.in === 'header' && requestData[p.name])
              .map(p => [p.name, requestData[p.name]]) || []
          )
        }
      };

      if (['POST', 'PUT', 'PATCH'].includes(endpoint.method.toUpperCase()) && endpoint.requestBody) {
        options.body = JSON.stringify(requestData.body || {});
      }

      const res = await fetch(url, options);
      const data = await res.json();
      
      setResponse({
        status: res.status,
        statusText: res.statusText,
        headers: Object.fromEntries(res.headers.entries()),
        data
      });
    } catch (error) {
      setResponse({
        status: 0,
        statusText: 'Network Error',
        headers: {},
        data: { error: error.message }
      });
    }
    setLoading(false);
  };

  return (
    <div className={styles.endpointDetails}>
      {/* Tabs */}
      <div className={styles.detailTabs}>
        <button 
          className={clsx(styles.tab, activeTab === 'try' && styles.activeTab)}
          onClick={() => setActiveTab('try')}
        >
          Try it out
        </button>
        <button 
          className={clsx(styles.tab, activeTab === 'schema' && styles.activeTab)}
          onClick={() => setActiveTab('schema')}
        >
          Schema
        </button>
      </div>

      {activeTab === 'try' && (
        <div className={styles.tryItOut}>
          {/* Parameters */}
          {endpoint.parameters && endpoint.parameters.length > 0 && (
            <div className={styles.parametersSection}>
              <h4>Parameters</h4>
              {endpoint.parameters.map((param) => (
                <div key={param.name} className={styles.parameter}>
                  <label className={styles.paramLabel}>
                    {param.name}
                    {param.required && <span className={styles.required}>*</span>}
                    <span className={styles.paramType}>({param.in})</span>
                  </label>
                  <input
                    type="text"
                    className={styles.paramInput}
                    placeholder={param.description || `Enter ${param.name}`}
                    value={requestData[param.name] || ''}
                    onChange={(e) => setRequestData({
                      ...requestData,
                      [param.name]: e.target.value
                    })}
                  />
                  {param.description && (
                    <p className={styles.paramDescription}>{param.description}</p>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Request Body */}
          {endpoint.requestBody && (
            <div className={styles.requestBodySection}>
              <h4>Request Body</h4>
              <textarea
                className={styles.requestBodyEditor}
                rows={10}
                placeholder={JSON.stringify(endpoint.requestBody.example || {}, null, 2)}
                value={JSON.stringify(requestData.body || {}, null, 2)}
                onChange={(e) => {
                  try {
                    setRequestData({
                      ...requestData,
                      body: JSON.parse(e.target.value)
                    });
                  } catch {
                    // Invalid JSON, keep as string for now
                  }
                }}
              />
            </div>
          )}

          {/* Execute Button */}
          <button 
            className={styles.executeBtn}
            onClick={executeRequest}
            disabled={loading}
          >
            {loading ? 'Executing...' : 'Execute'}
          </button>

          {/* Response */}
          {response && (
            <div className={styles.responseSection}>
              <h4>Response</h4>
              <div className={styles.responseHeader}>
                <span className={clsx(
                  styles.statusCode,
                  response.status >= 200 && response.status < 300 ? styles.success :
                  response.status >= 400 ? styles.error : styles.info
                )}>
                  {response.status} {response.statusText}
                </span>
              </div>
              <pre className={styles.responseBody}>
                {JSON.stringify(response.data, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}

      {activeTab === 'schema' && (
        <div className={styles.schemaTab}>
          <SchemaViewer schema={endpoint.requestBody} title="Request Schema" />
          {endpoint.responses && Object.entries(endpoint.responses).map(([code, response]) => (
            <SchemaViewer 
              key={code}
              schema={response.schema} 
              title={`Response ${code}`}
              description={response.description}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// Schema viewer component (similar to Stripe docs)
const SchemaViewer: React.FC<{ 
  schema?: Schema; 
  title: string; 
  description?: string;
}> = ({ schema, title, description }) => {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  if (!schema) return null;

  const toggleNode = (path: string) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedNodes(newExpanded);
  };

  const renderSchema = (schema: Schema, path = '', level = 0): React.ReactNode => {
    if (schema.type === 'object' && schema.properties) {
      return (
        <div className={styles.schemaObject} style={{ marginLeft: level * 20 }}>
          {Object.entries(schema.properties).map(([key, propSchema]) => {
            const currentPath = `${path}.${key}`;
            const isRequired = schema.required?.includes(key);
            const isExpanded = expandedNodes.has(currentPath);

            return (
              <div key={key} className={styles.schemaProperty}>
                <div 
                  className={styles.propertyHeader}
                  onClick={() => propSchema.properties && toggleNode(currentPath)}
                >
                  <span className={styles.propertyName}>
                    {key}
                    {isRequired && <span className={styles.required}>*</span>}
                  </span>
                  <span className={styles.propertyType}>{propSchema.type}</span>
                  {propSchema.properties && (
                    <span className={styles.expandIcon}>
                      {isExpanded ? '−' : '+'}
                    </span>
                  )}
                </div>
                {propSchema.description && (
                  <p className={styles.propertyDescription}>
                    {propSchema.description}
                  </p>
                )}
                {isExpanded && propSchema.properties && (
                  renderSchema(propSchema, currentPath, level + 1)
                )}
              </div>
            );
          })}
        </div>
      );
    }

    return null;
  };

  return (
    <div className={styles.schemaViewer}>
      <h4 className={styles.schemaTitle}>{title}</h4>
      {description && <p className={styles.schemaDescription}>{description}</p>}
      <div className={styles.schemaContent}>
        {renderSchema(schema)}
      </div>
      {schema.example && (
        <div className={styles.schemaExample}>
          <h5>Example</h5>
          <pre className={styles.exampleCode}>
            {JSON.stringify(schema.example, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default ApiExplorer;