import React, { useState } from 'react';
import CodeBlock from '@theme/CodeBlock';
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';
import styles from './styles.module.css';

// Language configurations
const LANGUAGES = [
  { id: 'typescript', name: 'TypeScript', extension: '.d.ts' },
  { id: 'python', name: 'Python', extension: '.py' },
  { id: 'java', name: 'Java', extension: '.java' },
  { id: 'csharp', name: 'C#', extension: '.cs' },
  { id: 'go', name: 'Go', extension: '.go' },
  { id: 'rust', name: 'Rust', extension: '.rs' },
  { id: 'swift', name: 'Swift', extension: '.swift' },
  { id: 'kotlin', name: 'Kotlin', extension: '.kt' },
];

const NAMING_CONVENTIONS = [
  { id: 'PascalCase_camelCase', name: 'PascalCase / camelCase', description: 'Standard TypeScript style' },
  { id: 'PascalCase_snake_case', name: 'PascalCase / snake_case', description: 'Mixed style' },
  { id: 'snake_case_snake_case', name: 'snake_case / snake_case', description: 'Python style' },
  { id: 'PascalCase_PascalCase', name: 'PascalCase / PascalCase', description: 'C# style' },
  { id: 'camelCase_camelCase', name: 'camelCase / camelCase', description: 'JavaScript style' },
  { id: 'kebab-case_kebab-case', name: 'kebab-case / kebab-case', description: 'CSS style' },
];

// Sample type definitions for demonstration
const SAMPLE_TYPES = {
  typescript: {
    'PascalCase_camelCase': `export interface ProductSerializer {
  readonly categoryName: string;
  readonly brandName: string;
  primaryImage: string;
  readonly currentPrice: number;
  readonly isOnSale: boolean;
  readonly discountPercentage: number;
}

export interface UserSerializer {
  fullName: string;
  email: string;
  isActive: boolean;
}`,
    'PascalCase_snake_case': `export interface ProductSerializer {
  readonly category_name: string;
  readonly brand_name: string;
  primary_image: string;
  readonly current_price: number;
  readonly is_on_sale: boolean;
  readonly discount_percentage: number;
}

export interface UserSerializer {
  full_name: string;
  email: string;
  is_active: boolean;
}`,
    'snake_case_snake_case': `export interface product_serializer {
  readonly category_name: string;
  readonly brand_name: string;
  primary_image: string;
  readonly current_price: number;
  readonly is_on_sale: boolean;
  readonly discount_percentage: number;
}

export interface user_serializer {
  full_name: string;
  email: string;
  is_active: boolean;
}`,
    'PascalCase_PascalCase': `export interface ProductSerializer {
  readonly CategoryName: string;
  readonly BrandName: string;
  PrimaryImage: string;
  readonly CurrentPrice: number;
  readonly IsOnSale: boolean;
  readonly DiscountPercentage: number;
}

export interface UserSerializer {
  FullName: string;
  Email: string;
  IsActive: boolean;
}`,
    'camelCase_camelCase': `export interface productSerializer {
  readonly categoryName: string;
  readonly brandName: string;
  primaryImage: string;
  readonly currentPrice: number;
  readonly isOnSale: boolean;
  readonly discountPercentage: number;
}

export interface userSerializer {
  fullName: string;
  email: string;
  isActive: boolean;
}`,
    'kebab-case_kebab-case': `export interface product-serializer {
  readonly category-name: string;
  readonly brand-name: string;
  primary-image: string;
  readonly current-price: number;
  readonly is-on-sale: boolean;
  readonly discount-percentage: number;
}

export interface user-serializer {
  full-name: string;
  email: string;
  is-active: boolean;
}`
  },
  python: {
    'PascalCase_snake_case': `@dataclass
class ProductSerializer:
    """Generated from ProductSerializer serializer"""
    category_name: str
    brand_name: str
    primary_image: str
    current_price: float
    is_on_sale: bool
    discount_percentage: float

@dataclass
class UserSerializer:
    """Generated from UserSerializer serializer"""
    full_name: str
    email: str
    is_active: bool`,
    'snake_case_snake_case': `@dataclass
class product_serializer:
    """Generated from ProductSerializer serializer"""
    category_name: str
    brand_name: str
    primary_image: str
    current_price: float
    is_on_sale: bool
    discount_percentage: float

@dataclass
class user_serializer:
    """Generated from UserSerializer serializer"""
    full_name: str
    email: str
    is_active: bool`,
    'PascalCase_camelCase': `@dataclass
class ProductSerializer:
    """Generated from ProductSerializer serializer"""
    categoryName: str
    brandName: str
    primaryImage: str
    currentPrice: float
    isOnSale: bool
    discountPercentage: float

@dataclass
class UserSerializer:
    """Generated from UserSerializer serializer"""
    fullName: str
    email: str
    isActive: bool`
  },
  java: {
    'PascalCase_camelCase': `public class ProductSerializer {
    private String categoryName;
    private String brandName;
    private String primaryImage;
    private Double currentPrice;
    private Boolean isOnSale;
    private Double discountPercentage;
    
    // Getters and setters...
}

public class UserSerializer {
    private String fullName;
    private String email;
    private Boolean isActive;
    
    // Getters and setters...
}`,
    'PascalCase_snake_case': `public class ProductSerializer {
    private String category_name;
    private String brand_name;
    private String primary_image;
    private Double current_price;
    private Boolean is_on_sale;
    private Double discount_percentage;
    
    // Getters and setters...
}

public class UserSerializer {
    private String full_name;
    private String email;
    private Boolean is_active;
    
    // Getters and setters...
}`
  },
  csharp: {
    'PascalCase_PascalCase': `public class ProductSerializer 
{
    public string CategoryName { get; set; }
    public string BrandName { get; set; }
    public string PrimaryImage { get; set; }
    public decimal CurrentPrice { get; set; }
    public bool IsOnSale { get; set; }
    public decimal DiscountPercentage { get; set; }
}

public class UserSerializer 
{
    public string FullName { get; set; }
    public string Email { get; set; }
    public bool IsActive { get; set; }
}`,
    'PascalCase_camelCase': `public class ProductSerializer 
{
    public string categoryName { get; set; }
    public string brandName { get; set; }
    public string primaryImage { get; set; }
    public decimal currentPrice { get; set; }
    public bool isOnSale { get; set; }
    public decimal discountPercentage { get; set; }
}

public class UserSerializer 
{
    public string fullName { get; set; }
    public string email { get; set; }
    public bool isActive { get; set; }
}`
  }
};

interface MultiLanguageTypeViewerProps {
  appName: string;
  title?: string;
}

export default function MultiLanguageTypeViewer({ appName, title = "API Type Definitions" }: MultiLanguageTypeViewerProps) {
  const [selectedNaming, setSelectedNaming] = useState('PascalCase_camelCase');

  return (
    <div className={styles.multiLanguageViewer}>
      <div className={styles.header}>
        <h3>{title}</h3>
        <p>Choose your preferred language and naming convention:</p>
      </div>

      {/* Naming Convention Selector */}
      <div className={styles.namingSelector}>
        <label htmlFor="naming-select">Naming Convention:</label>
        <select 
          id="naming-select"
          value={selectedNaming} 
          onChange={(e) => setSelectedNaming(e.target.value)}
          className={styles.select}
        >
          {NAMING_CONVENTIONS.map(convention => (
            <option key={convention.id} value={convention.id}>
              {convention.name} - {convention.description}
            </option>
          ))}
        </select>
      </div>

      {/* Language Tabs */}
      <Tabs groupId="programming-languages" defaultValue="typescript">
        {LANGUAGES.map(language => {
          const hasContent = SAMPLE_TYPES[language.id] && SAMPLE_TYPES[language.id][selectedNaming];
          
          return (
            <TabItem key={language.id} value={language.id} label={language.name}>
              <div className={styles.languageContent}>
                <div className={styles.languageHeader}>
                  <span className={styles.languageIcon}>📄</span>
                  <span className={styles.fileName}>
                    {appName}{language.extension}
                  </span>
                  <a 
                    href={`/types_multi/${language.id}/${selectedNaming}/`}
                    className={styles.downloadLink}
                    target="_blank"
                  >
                    📁 View Generated Files
                  </a>
                </div>
                
                {hasContent ? (
                  <CodeBlock language={language.id === 'csharp' ? 'csharp' : language.id}>
                    {SAMPLE_TYPES[language.id][selectedNaming]}
                  </CodeBlock>
                ) : (
                  <div className={styles.placeholder}>
                    <p>Generated {language.name} types available in:</p>
                    <code>easy_sdk/types_multi/{language.id}/{selectedNaming}/</code>
                  </div>
                )}
              </div>
            </TabItem>
          );
        })}
      </Tabs>

      {/* Download Section */}
      <div className={styles.downloadSection}>
        <h4>📦 Complete Type Package</h4>
        <p>All generated types are available in the <code>easy_sdk/types_multi/</code> directory:</p>
        <ul>
          <li><strong>8 Programming Languages:</strong> TypeScript, Python, Java, C#, Go, Rust, Swift, Kotlin</li>
          <li><strong>36 Naming Variants:</strong> Every combination of interface and property naming conventions</li>
          <li><strong>Complete Documentation:</strong> README files and usage examples for each variant</li>
        </ul>
        
        <div className={styles.usageExample}>
          <h5>Usage Example:</h5>
          <CodeBlock language="bash">
            {`# Import TypeScript types with your preferred naming
import { ProductSerializer, UserSerializer } from './easy_sdk/types_multi/typescript/${selectedNaming}';

# Or use Python dataclasses
from easy_sdk.types_multi.python.${selectedNaming} import ProductSerializer, UserSerializer`}
          </CodeBlock>
        </div>
      </div>
    </div>
  );
}