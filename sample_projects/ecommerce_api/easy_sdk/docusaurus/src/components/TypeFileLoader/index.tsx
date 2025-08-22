import React, { useState, useEffect } from 'react';
import CodeBlock from '@theme/CodeBlock';
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

interface TypeFileLoaderProps {
  appName: string;
  namingConvention?: string;
  showLanguages?: string[];
}

// Load type definitions from the generated files
const loadTypeFile = async (language: string, naming: string, appName: string) => {
  try {
    // In a real implementation, this would fetch the actual generated files
    // For now, we'll simulate loading from our generated directory structure
    const response = await fetch(`/easy_sdk/types_multi/${language}/${naming}/${appName}.d.ts`);
    if (response.ok) {
      return await response.text();
    }
  } catch (error) {
    console.log(`File not found: ${language}/${naming}/${appName}`);
  }
  return null;
};

// Fallback content for when files aren't available
const getFallbackContent = (language: string, naming: string, appName: string) => {
  const conventions = naming.split('_');
  const interfaceNaming = conventions[0] || 'PascalCase';
  const propertyNaming = conventions[1] || 'camelCase';

  const sampleData = {
    typescript: `// Generated TypeScript definitions for ${appName}
// Interface naming: ${interfaceNaming}, Property naming: ${propertyNaming}

export interface ${interfaceNaming === 'PascalCase' ? 'ProductSerializer' : 'product_serializer'} {
  readonly ${propertyNaming === 'camelCase' ? 'categoryName' : 'category_name'}: string;
  readonly ${propertyNaming === 'camelCase' ? 'brandName' : 'brand_name'}: string;
  ${propertyNaming === 'camelCase' ? 'primaryImage' : 'primary_image'}: string;
  readonly ${propertyNaming === 'camelCase' ? 'currentPrice' : 'current_price'}: number;
  readonly ${propertyNaming === 'camelCase' ? 'isOnSale' : 'is_on_sale'}: boolean;
  readonly ${propertyNaming === 'camelCase' ? 'discountPercentage' : 'discount_percentage'}: number;
}

export interface ${interfaceNaming === 'PascalCase' ? 'CategorySerializer' : 'category_serializer'} {
  children: any;
  readonly ${propertyNaming === 'camelCase' ? 'parentName' : 'parent_name'}: string;
}`,
    python: `# Generated Python dataclasses for ${appName}
# Class naming: ${interfaceNaming}, Property naming: ${propertyNaming}

from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class ${interfaceNaming === 'PascalCase' ? 'ProductSerializer' : 'product_serializer'}:
    """Generated from ProductSerializer serializer"""
    ${propertyNaming === 'camelCase' ? 'categoryName' : 'category_name'}: str
    ${propertyNaming === 'camelCase' ? 'brandName' : 'brand_name'}: str
    ${propertyNaming === 'camelCase' ? 'primaryImage' : 'primary_image'}: str
    ${propertyNaming === 'camelCase' ? 'currentPrice' : 'current_price'}: float
    ${propertyNaming === 'camelCase' ? 'isOnSale' : 'is_on_sale'}: bool
    ${propertyNaming === 'camelCase' ? 'discountPercentage' : 'discount_percentage'}: float

@dataclass
class ${interfaceNaming === 'PascalCase' ? 'CategorySerializer' : 'category_serializer'}:
    """Generated from CategorySerializer serializer"""
    children: Any
    ${propertyNaming === 'camelCase' ? 'parentName' : 'parent_name'}: str`,
    java: `// Generated Java classes for ${appName}
// Class naming: ${interfaceNaming}, Property naming: ${propertyNaming}

public class ${interfaceNaming === 'PascalCase' ? 'ProductSerializer' : 'product_serializer'} {
    private String ${propertyNaming === 'camelCase' ? 'categoryName' : 'category_name'};
    private String ${propertyNaming === 'camelCase' ? 'brandName' : 'brand_name'};
    private String ${propertyNaming === 'camelCase' ? 'primaryImage' : 'primary_image'};
    private Double ${propertyNaming === 'camelCase' ? 'currentPrice' : 'current_price'};
    private Boolean ${propertyNaming === 'camelCase' ? 'isOnSale' : 'is_on_sale'};
    private Double ${propertyNaming === 'camelCase' ? 'discountPercentage' : 'discount_percentage'};
    
    // Getters and setters omitted for brevity
}`
  };

  return sampleData[language] || `// Generated ${language} code for ${appName} with ${naming} naming convention`;
};

export default function TypeFileLoader({ 
  appName, 
  namingConvention = 'PascalCase_camelCase',
  showLanguages = ['typescript', 'python', 'java']
}: TypeFileLoaderProps) {
  const [content, setContent] = useState<{[key: string]: string}>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadContent = async () => {
      setLoading(true);
      const newContent: {[key: string]: string} = {};

      for (const language of showLanguages) {
        try {
          const fileContent = await loadTypeFile(language, namingConvention, appName);
          newContent[language] = fileContent || getFallbackContent(language, namingConvention, appName);
        } catch (error) {
          newContent[language] = getFallbackContent(language, namingConvention, appName);
        }
      }

      setContent(newContent);
      setLoading(false);
    };

    loadContent();
  }, [appName, namingConvention, showLanguages]);

  if (loading) {
    return <div>Loading type definitions...</div>;
  }

  const getLanguageSyntax = (language: string) => {
    const syntaxMap = {
      'typescript': 'typescript',
      'python': 'python',
      'java': 'java',
      'csharp': 'csharp',
      'go': 'go',
      'rust': 'rust',
      'swift': 'swift',
      'kotlin': 'kotlin'
    };
    return syntaxMap[language] || 'text';
  };

  return (
    <div style={{ margin: '1rem 0' }}>
      <Tabs groupId="type-languages" defaultValue={showLanguages[0]}>
        {showLanguages.map(language => (
          <TabItem 
            key={language} 
            value={language} 
            label={language.charAt(0).toUpperCase() + language.slice(1)}
          >
            <div style={{ marginBottom: '1rem', padding: '0.5rem', backgroundColor: 'var(--ifm-color-emphasis-100)', borderRadius: '4px' }}>
              <small>
                <strong>📁 File:</strong> <code>types_multi/{language}/{namingConvention}/{appName}.{getFileExtension(language)}</code>
              </small>
            </div>
            <CodeBlock language={getLanguageSyntax(language)}>
              {content[language] || `// Loading ${language} definitions...`}
            </CodeBlock>
          </TabItem>
        ))}
      </Tabs>
    </div>
  );
}

function getFileExtension(language: string): string {
  const extensions = {
    'typescript': 'd.ts',
    'python': 'py',
    'java': 'java',
    'csharp': 'cs',
    'go': 'go',
    'rust': 'rs',
    'swift': 'swift',
    'kotlin': 'kt'
  };
  return extensions[language] || 'txt';
}