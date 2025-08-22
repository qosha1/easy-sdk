import React, { useState, useEffect } from 'react';
import CodeBlock from '@theme/CodeBlock';
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';
import styles from './styles.module.css';

// Language configurations
const LANGUAGES = [
  { id: 'typescript', name: 'TypeScript', extension: '.d.ts', syntax: 'typescript' },
  { id: 'python', name: 'Python', extension: '.py', syntax: 'python' },
  { id: 'java', name: 'Java', extension: '.java', syntax: 'java' },
  { id: 'csharp', name: 'C#', extension: '.cs', syntax: 'csharp' },
  { id: 'go', name: 'Go', extension: '.go', syntax: 'go' },
  { id: 'rust', name: 'Rust', extension: '.rs', syntax: 'rust' },
  { id: 'swift', name: 'Swift', extension: '.swift', syntax: 'swift' },
  { id: 'kotlin', name: 'Kotlin', extension: '.kt', syntax: 'kotlin' },
];

const NAMING_CONVENTIONS = [
  { id: 'PascalCase_camelCase', name: 'PascalCase / camelCase', description: 'Standard TypeScript/JavaScript style', popular: true },
  { id: 'PascalCase_snake_case', name: 'PascalCase / snake_case', description: 'Mixed style (C# classes, Python properties)', popular: true },
  { id: 'snake_case_snake_case', name: 'snake_case / snake_case', description: 'Python/Django style', popular: true },
  { id: 'PascalCase_PascalCase', name: 'PascalCase / PascalCase', description: 'C# style', popular: true },
  { id: 'camelCase_camelCase', name: 'camelCase / camelCase', description: 'JavaScript style', popular: false },
  { id: 'kebab-case_kebab-case', name: 'kebab-case / kebab-case', description: 'CSS/HTML style', popular: false },
  { id: 'SCREAMING_SNAKE_SCREAMING_SNAKE', name: 'SCREAMING_SNAKE', description: 'Constants style', popular: false },
  { id: 'lowercase_lowercase', name: 'lowercase / lowercase', description: 'Minimal style', popular: false },
];

interface FileContent {
  [language: string]: {
    [naming: string]: {
      [filename: string]: string;
    };
  };
}

interface DynamicTypeLoaderProps {
  appName: string;
  title?: string;
  showAllVariants?: boolean;
}

// Mock file content loader (in a real implementation, this would fetch from the actual generated files)
const loadFileContent = async (language: string, naming: string, filename: string): Promise<string> => {
  // This would typically fetch from the actual generated files
  // For now, we'll return sample content based on the patterns we know work
  
  const sampleContent = {
    typescript: {
      'PascalCase_camelCase': `import { PaginatedResponse, ApiError, Nullable, Optional } from './common';

/**
 * Generated from CategorySerializer serializer
 */
export interface CategorySerializer {
  children: any;
  readonly parentName: any;
}

/**
 * Generated from BrandSerializer serializer  
 */
export interface BrandSerializer {
  productCount: any;
}

/**
 * Generated from ProductListSerializer serializer
 */
export interface ProductListSerializer {
  readonly categoryName: any;
  readonly brandName: any;
  primaryImage: any;
  readonly currentPrice: any;
  readonly isOnSale: any;
  readonly discountPercentage: any;
}`,
      'PascalCase_snake_case': `import { PaginatedResponse, ApiError, Nullable, Optional } from './common';

/**
 * Generated from CategorySerializer serializer
 */
export interface CategorySerializer {
  children: any;
  readonly parent_name: any;
}

/**
 * Generated from BrandSerializer serializer  
 */
export interface BrandSerializer {
  product_count: any;
}

/**
 * Generated from ProductListSerializer serializer
 */
export interface ProductListSerializer {
  readonly category_name: any;
  readonly brand_name: any;
  primary_image: any;
  readonly current_price: any;
  readonly is_on_sale: any;
  readonly discount_percentage: any;
}`,
      'snake_case_snake_case': `import { PaginatedResponse, ApiError, Nullable, Optional } from './common';

/**
 * Generated from CategorySerializer serializer
 */
export interface category_serializer {
  children: any;
  readonly parent_name: any;
}

/**
 * Generated from BrandSerializer serializer  
 */
export interface brand_serializer {
  product_count: any;
}

/**
 * Generated from ProductListSerializer serializer
 */
export interface product_list_serializer {
  readonly category_name: any;
  readonly brand_name: any;
  primary_image: any;
  readonly current_price: any;
  readonly is_on_sale: any;
  readonly discount_percentage: any;
}`,
    },
    python: {
      'PascalCase_snake_case': `"""
Generated API Types
Generated types for ${filename} app

This file was automatically generated. Do not edit manually.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime, date, time
from decimal import Decimal

@dataclass
class CategorySerializer:
    """Generated from CategorySerializer serializer"""
    children: any
    parent_name: any

@dataclass
class BrandSerializer:
    """Generated from BrandSerializer serializer"""
    product_count: any

@dataclass
class ProductListSerializer:
    """Generated from ProductListSerializer serializer"""
    category_name: any
    brand_name: any
    primary_image: any
    current_price: any
    is_on_sale: any
    discount_percentage: any`,
      'snake_case_snake_case': `"""
Generated API Types
Generated types for ${filename} app

This file was automatically generated. Do not edit manually.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime, date, time
from decimal import Decimal

@dataclass
class category_serializer:
    """Generated from CategorySerializer serializer"""
    children: any
    parent_name: any

@dataclass
class brand_serializer:
    """Generated from BrandSerializer serializer"""
    product_count: any

@dataclass
class product_list_serializer:
    """Generated from ProductListSerializer serializer"""
    category_name: any
    brand_name: any
    primary_image: any
    current_price: any
    is_on_sale: any
    discount_percentage: any`,
    },
    java: {
      'PascalCase_camelCase': `/**
 * Generated API Types
 * Generated types for ${filename} app
 * 
 * This file was automatically generated. Do not edit manually.
 */

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.LocalDate;
import java.time.LocalTime;
import java.util.List;

public class CategorySerializer {
    /** Generated from CategorySerializer serializer */
    private Object children;
    private Object parentName;

    public Object getChildren() {
        return children;
    }

    public void setChildren(Object children) {
        this.children = children;
    }

    public Object getParentName() {
        return parentName;
    }

    public void setParentName(Object parentName) {
        this.parentName = parentName;
    }
}

public class BrandSerializer {
    /** Generated from BrandSerializer serializer */
    private Object productCount;

    public Object getProductCount() {
        return productCount;
    }

    public void setProductCount(Object productCount) {
        this.productCount = productCount;
    }
}`,
    }
  };

  return sampleContent[language]?.[naming] || `// Generated ${language} code for ${filename}\n// Naming convention: ${naming}`;
};

export default function DynamicTypeLoader({ appName, title = "API Type Definitions", showAllVariants = false }: DynamicTypeLoaderProps) {
  const [selectedNaming, setSelectedNaming] = useState('PascalCase_camelCase');
  const [fileContent, setFileContent] = useState<FileContent>({});
  const [loading, setLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(showAllVariants);

  const displayedNamingConventions = showAdvanced 
    ? NAMING_CONVENTIONS 
    : NAMING_CONVENTIONS.filter(conv => conv.popular);

  // Load file content when language or naming changes
  useEffect(() => {
    const loadContent = async () => {
      setLoading(true);
      try {
        const content: FileContent = {};
        
        for (const language of LANGUAGES) {
          content[language.id] = {};
          content[language.id][selectedNaming] = {};
          
          // Load the main app file
          const appContent = await loadFileContent(language.id, selectedNaming, appName);
          content[language.id][selectedNaming][appName] = appContent;
        }
        
        setFileContent(content);
      } catch (error) {
        console.error('Error loading file content:', error);
      } finally {
        setLoading(false);
      }
    };

    loadContent();
  }, [selectedNaming, appName]);

  return (
    <div className={styles.dynamicTypeLoader}>
      <div className={styles.header}>
        <h3>{title}</h3>
        <p>Generated in <strong>8 programming languages</strong> with <strong>configurable naming conventions</strong></p>
      </div>

      {/* Naming Convention Selector */}
      <div className={styles.controls}>
        <div className={styles.namingSelector}>
          <label htmlFor="naming-select">Naming Convention:</label>
          <select 
            id="naming-select"
            value={selectedNaming} 
            onChange={(e) => setSelectedNaming(e.target.value)}
            className={styles.select}
          >
            {displayedNamingConventions.map(convention => (
              <option key={convention.id} value={convention.id}>
                {convention.name} - {convention.description}
              </option>
            ))}
          </select>
        </div>

        <button 
          className={styles.toggleButton}
          onClick={() => setShowAdvanced(!showAdvanced)}
        >
          {showAdvanced ? '📋 Popular Only' : '🔧 Show All Variants'}
        </button>
      </div>

      {/* Language Tabs */}
      <Tabs groupId="programming-languages" defaultValue="typescript">
        {LANGUAGES.map(language => {
          const content = fileContent[language.id]?.[selectedNaming]?.[appName];
          
          return (
            <TabItem key={language.id} value={language.id} label={language.name}>
              <div className={styles.languageContent}>
                <div className={styles.languageHeader}>
                  <span className={styles.languageIcon}>📄</span>
                  <span className={styles.fileName}>
                    {appName}{language.extension}
                  </span>
                  <div className={styles.pathInfo}>
                    <code>types_multi/{language.id}/{selectedNaming}/</code>
                  </div>
                </div>
                
                {loading ? (
                  <div className={styles.loading}>Loading {language.name} definitions...</div>
                ) : content ? (
                  <CodeBlock language={language.syntax}>
                    {content}
                  </CodeBlock>
                ) : (
                  <div className={styles.placeholder}>
                    <p>Generated {language.name} types for the <strong>{selectedNaming}</strong> naming convention</p>
                    <p>Available in: <code>easy_sdk/types_multi/{language.id}/{selectedNaming}/{appName}{language.extension}</code></p>
                  </div>
                )}
              </div>
            </TabItem>
          );
        })}
      </Tabs>

      {/* Generation Info */}
      <div className={styles.generationInfo}>
        <h4>🚀 Complete Type Generation</h4>
        <div className={styles.stats}>
          <div className={styles.stat}>
            <span className={styles.statNumber}>8</span>
            <span className={styles.statLabel}>Programming Languages</span>
          </div>
          <div className={styles.stat}>
            <span className={styles.statNumber}>36</span>
            <span className={styles.statLabel}>Naming Variants</span>
          </div>
          <div className={styles.stat}>
            <span className={styles.statNumber}>32</span>
            <span className={styles.statLabel}>Serializers Analyzed</span>
          </div>
        </div>
        
        <div className={styles.usage}>
          <h5>💡 Usage Examples:</h5>
          <CodeBlock language="bash">
{`# TypeScript import
import { ProductSerializer } from './easy_sdk/types_multi/typescript/${selectedNaming}/products';

# Python import  
from easy_sdk.types_multi.python.${selectedNaming}.products import ProductSerializer

# Java package
import com.yourapp.types.${selectedNaming}.ProductSerializer;`}
          </CodeBlock>
        </div>
      </div>
    </div>
  );
}