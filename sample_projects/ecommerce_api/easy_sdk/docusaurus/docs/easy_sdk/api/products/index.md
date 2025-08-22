---
sidebar_position: 1
---

# Products API

The Products API provides endpoints for managing product catalogs, categories, brands, and product images in the e-commerce system.

## Overview

The products module includes the following main components:

- **Categories** - Hierarchical product categorization
- **Brands** - Product brand management  
- **Products** - Core product catalog with pricing and inventory
- **Product Images** - Image management for products

## Endpoints

### Categories

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/categories/` | List all categories |
| POST | `/api/categories/` | Create a new category |
| GET | `/api/categories/{slug}/` | Get category details |
| PUT | `/api/categories/{slug}/` | Update category |
| DELETE | `/api/categories/{slug}/` | Delete category |
| GET | `/api/categories/{slug}/products/` | Get products in category |
| GET | `/api/categories/{slug}/subcategories/` | Get subcategories |

### Brands

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/brands/` | List all brands |
| POST | `/api/brands/` | Create a new brand |
| GET | `/api/brands/{slug}/` | Get brand details |
| PUT | `/api/brands/{slug}/` | Update brand |
| DELETE | `/api/brands/{slug}/` | Delete brand |
| GET | `/api/brands/{slug}/products/` | Get products from brand |

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products/` | List all products |
| POST | `/api/products/` | Create a new product |
| GET | `/api/products/{slug}/` | Get product details |
| PUT | `/api/products/{slug}/` | Update product |
| DELETE | `/api/products/{slug}/` | Delete product |
| GET | `/api/products/featured/` | Get featured products |
| GET | `/api/products/on_sale/` | Get products on sale |
| POST | `/api/products/search/` | Advanced product search |
| POST | `/api/products/{slug}/add_image/` | Add product image |
| DELETE | `/api/products/{slug}/remove_image/` | Remove product image |
| PATCH | `/api/products/{slug}/update_stock/` | Update stock quantity |
| PATCH | `/api/products/{slug}/toggle_featured/` | Toggle featured status |

### Product Images

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/product-images/` | List product images |
| POST | `/api/product-images/` | Upload new image |
| GET | `/api/product-images/{id}/` | Get image details |
| PUT | `/api/product-images/{id}/` | Update image |
| DELETE | `/api/product-images/{id}/` | Delete image |
| PATCH | `/api/product-images/{id}/set_primary/` | Set as primary image |

## Data Models

import DynamicTypeLoader from '@site/src/components/DynamicTypeLoader';

<DynamicTypeLoader 
  appName="products"
  title="Products App Data Models"
  showAllVariants={false}
/>

### Model Summary

The Products app includes the following serializers:
- **CategorySerializer**: 2 fields
- **BrandSerializer**: 1 fields  
- **ProductImageSerializer**: 0 fields
- **ProductListSerializer**: 6 fields
- **ProductDetailSerializer**: 10 fields
- **ProductCreateUpdateSerializer**: 1 fields
- **ProductSearchSerializer**: 9 fields

### 🎯 Why Multiple Languages & Naming Conventions?

Different development environments have different conventions:

- **Frontend Teams**: Often prefer `camelCase` properties for JavaScript/TypeScript
- **Backend Teams**: May prefer `snake_case` to match Python/Django conventions  
- **Mobile Teams**: iOS uses `PascalCase`, Android varies by language
- **Integration Teams**: Need to match existing codebases and style guides

Easy-SDK generates **all variants automatically** so every team can use their preferred style without manual conversion.

## Filtering and Search

### Query Parameters

- `search` - Text search across name, description, SKU
- `category` - Filter by category ID
- `brand` - Filter by brand ID  
- `price__gte` - Minimum price filter
- `price__lte` - Maximum price filter
- `featured` - Filter featured products
- `status` - Filter by status (active, inactive, draft)
- `ordering` - Sort by fields (name, price, created_at, etc.)

### Example Requests

```bash
# Get featured products
GET /api/products/?featured=true

# Search for products
GET /api/products/?search=wireless&category=1

# Get products on sale under $100
GET /api/products/on_sale/?price__lte=100
```

## Authentication

Most endpoints require authentication. Product creation, updates, and deletions require staff permissions.