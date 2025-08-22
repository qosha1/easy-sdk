---
sidebar_position: 1
---

# Products API

import SwaggerApiDocs from '@site/src/components/SwaggerApiDocs';

<SwaggerApiDocs 
  appName="products"
  title="Products API"
  description="The Products API provides endpoints for managing product catalogs, categories, brands, and product images in the e-commerce system. This includes hierarchical product categorization, brand management, product catalog with pricing and inventory, and image management."
  serializers={[
    {
      name: 'CategorySerializer',
      fields: {
        id: { type: 'IntegerField', required: false, read_only: true, help_text: 'Category ID' },
        name: { type: 'CharField', required: true, max_length: 200, help_text: 'Category name' },
        slug: { type: 'SlugField', required: false, read_only: true, help_text: 'URL-friendly category identifier' },
        description: { type: 'TextField', required: false, help_text: 'Category description' },
        parent: { type: 'ForeignKey', required: false, help_text: 'Parent category (for hierarchical structure)' },
        image: { type: 'ImageField', required: false, help_text: 'Category image' },
        is_active: { type: 'BooleanField', required: false, help_text: 'Whether category is active' },
        sort_order: { type: 'IntegerField', required: false, help_text: 'Display order' }
      },
      docstring: 'Product category information with hierarchical support'
    },
    {
      name: 'BrandSerializer', 
      fields: {
        id: { type: 'IntegerField', required: false, read_only: true, help_text: 'Brand ID' },
        name: { type: 'CharField', required: true, max_length: 100, help_text: 'Brand name' },
        slug: { type: 'SlugField', required: false, read_only: true, help_text: 'URL-friendly brand identifier' },
        description: { type: 'TextField', required: false, help_text: 'Brand description' },
        logo: { type: 'ImageField', required: false, help_text: 'Brand logo image' },
        website: { type: 'URLField', required: false, help_text: 'Brand website URL' },
        is_active: { type: 'BooleanField', required: false, help_text: 'Whether brand is active' }
      },
      docstring: 'Product brand information'
    },
    {
      name: 'ProductSerializer',
      fields: {
        id: { type: 'IntegerField', required: false, read_only: true, help_text: 'Product ID' },
        name: { type: 'CharField', required: true, max_length: 200, help_text: 'Product name' },
        slug: { type: 'SlugField', required: false, read_only: true, help_text: 'URL-friendly product identifier' },
        description: { type: 'TextField', required: false, help_text: 'Product description' },
        short_description: { type: 'CharField', required: false, max_length: 500, help_text: 'Brief product description' },
        price: { type: 'DecimalField', required: true, help_text: 'Product price' },
        sale_price: { type: 'DecimalField', required: false, help_text: 'Sale/discounted price' },
        sku: { type: 'CharField', required: true, max_length: 100, help_text: 'Stock keeping unit' },
        category: { type: 'ForeignKey', required: true, help_text: 'Product category' },
        brand: { type: 'ForeignKey', required: false, help_text: 'Product brand' },
        stock_quantity: { type: 'IntegerField', required: false, help_text: 'Available stock quantity' },
        weight: { type: 'DecimalField', required: false, help_text: 'Product weight' },
        dimensions: { type: 'CharField', required: false, max_length: 100, help_text: 'Product dimensions' },
        is_active: { type: 'BooleanField', required: false, help_text: 'Whether product is active' },
        is_featured: { type: 'BooleanField', required: false, help_text: 'Whether product is featured' },
        created_date: { type: 'DateTimeField', required: false, read_only: true, help_text: 'Creation timestamp' },
        updated_date: { type: 'DateTimeField', required: false, read_only: true, help_text: 'Last update timestamp' }
      },
      docstring: 'Complete product information with pricing and inventory'
    },
    {
      name: 'ProductImageSerializer',
      fields: {
        id: { type: 'IntegerField', required: false, read_only: true, help_text: 'Image ID' },
        product: { type: 'ForeignKey', required: true, help_text: 'Product this image belongs to' },
        image: { type: 'ImageField', required: true, help_text: 'Product image file' },
        alt_text: { type: 'CharField', required: false, max_length: 200, help_text: 'Alternative text for image' },
        is_primary: { type: 'BooleanField', required: false, help_text: 'Whether this is the primary product image' },
        sort_order: { type: 'IntegerField', required: false, help_text: 'Display order' }
      },
      docstring: 'Product image with metadata'
    }
  ]}
  endpoints={[
    // Categories
    { method: 'GET', path: '/api/categories/', description: 'List all categories', serializer_class: 'CategorySerializer', tags: ['Categories'] },
    { method: 'POST', path: '/api/categories/', description: 'Create a new category', serializer_class: 'CategorySerializer', tags: ['Categories'] },
    { method: 'GET', path: '/api/categories/{slug}/', description: 'Get category details', serializer_class: 'CategorySerializer', tags: ['Categories'] },
    { method: 'PUT', path: '/api/categories/{slug}/', description: 'Update category', serializer_class: 'CategorySerializer', tags: ['Categories'] },
    { method: 'DELETE', path: '/api/categories/{slug}/', description: 'Delete category', tags: ['Categories'] },
    { method: 'GET', path: '/api/categories/{slug}/products/', description: 'Get products in category', serializer_class: 'ProductSerializer', tags: ['Categories'] },
    { method: 'GET', path: '/api/categories/{slug}/subcategories/', description: 'Get subcategories', serializer_class: 'CategorySerializer', tags: ['Categories'] },
    
    // Brands
    { method: 'GET', path: '/api/brands/', description: 'List all brands', serializer_class: 'BrandSerializer', tags: ['Brands'] },
    { method: 'POST', path: '/api/brands/', description: 'Create a new brand', serializer_class: 'BrandSerializer', tags: ['Brands'] },
    { method: 'GET', path: '/api/brands/{slug}/', description: 'Get brand details', serializer_class: 'BrandSerializer', tags: ['Brands'] },
    { method: 'PUT', path: '/api/brands/{slug}/', description: 'Update brand', serializer_class: 'BrandSerializer', tags: ['Brands'] },
    { method: 'DELETE', path: '/api/brands/{slug}/', description: 'Delete brand', tags: ['Brands'] },
    { method: 'GET', path: '/api/brands/{slug}/products/', description: 'Get products from brand', serializer_class: 'ProductSerializer', tags: ['Brands'] },
    
    // Products
    { method: 'GET', path: '/api/products/', description: 'List all products with pagination and filtering', serializer_class: 'ProductSerializer', tags: ['Products'] },
    { method: 'POST', path: '/api/products/', description: 'Create a new product', serializer_class: 'ProductSerializer', tags: ['Products'] },
    { method: 'GET', path: '/api/products/{slug}/', description: 'Get product details', serializer_class: 'ProductSerializer', tags: ['Products'] },
    { method: 'PUT', path: '/api/products/{slug}/', description: 'Update product', serializer_class: 'ProductSerializer', tags: ['Products'] },
    { method: 'DELETE', path: '/api/products/{slug}/', description: 'Delete product', tags: ['Products'] },
    { method: 'GET', path: '/api/products/featured/', description: 'Get featured products', serializer_class: 'ProductSerializer', tags: ['Products'] },
    { method: 'GET', path: '/api/products/on_sale/', description: 'Get products on sale', serializer_class: 'ProductSerializer', tags: ['Products'] },
    { method: 'POST', path: '/api/products/search/', description: 'Advanced product search', serializer_class: 'ProductSerializer', tags: ['Products'] },
    { method: 'POST', path: '/api/products/{slug}/add_image/', description: 'Add product image', serializer_class: 'ProductImageSerializer', tags: ['Products'] },
    { method: 'DELETE', path: '/api/products/{slug}/remove_image/', description: 'Remove product image', tags: ['Products'] },
    { method: 'PATCH', path: '/api/products/{slug}/update_stock/', description: 'Update stock quantity', tags: ['Products'] },
    { method: 'PATCH', path: '/api/products/{slug}/toggle_featured/', description: 'Toggle featured status', tags: ['Products'] },
    
    // Product Images
    { method: 'GET', path: '/api/product-images/', description: 'List product images', serializer_class: 'ProductImageSerializer', tags: ['Product Images'] },
    { method: 'POST', path: '/api/product-images/', description: 'Upload new image', serializer_class: 'ProductImageSerializer', tags: ['Product Images'] },
    { method: 'GET', path: '/api/product-images/{id}/', description: 'Get image details', serializer_class: 'ProductImageSerializer', tags: ['Product Images'] },
    { method: 'PUT', path: '/api/product-images/{id}/', description: 'Update image', serializer_class: 'ProductImageSerializer', tags: ['Product Images'] },
    { method: 'DELETE', path: '/api/product-images/{id}/', description: 'Delete image', tags: ['Product Images'] },
    { method: 'PATCH', path: '/api/product-images/{id}/set_primary/', description: 'Set as primary image', tags: ['Product Images'] }
  ]}
/>

## Quick Examples

### Create a New Product

```bash
POST /api/products/
Authorization: Bearer your-token-here
Content-Type: application/json

{
  "name": "Premium Wireless Headphones",
  "description": "High-quality wireless headphones with noise cancellation",
  "short_description": "Premium wireless headphones",
  "price": "199.99",
  "sku": "WHD-001",
  "category": 1,
  "brand": 2,
  "stock_quantity": 50,
  "weight": "0.5",
  "is_featured": true
}
```

### Search Products

```bash
POST /api/products/search/
Authorization: Bearer your-token-here
Content-Type: application/json

{
  "query": "headphones",
  "category": "electronics",
  "min_price": 50,
  "max_price": 300,
  "brand": "sony"
}
```

## Legacy Documentation

import DynamicTypeLoader from '@site/src/components/DynamicTypeLoader';

<DynamicTypeLoader 
  appName="products"
  title="Products App Data Models"
  showAllVariants={false}
/>