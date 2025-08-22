import { PaginatedResponse, ApiError, Nullable, Optional } from './common';

/**
 * Generated API Types
 * Generated types for products app
 * 
 * This file was automatically generated. Do not edit manually.
 */


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
 * Generated from ProductImageSerializer serializer
 */
export interface ProductImageSerializer {
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
}


/**
 * Generated from ProductDetailSerializer serializer
 */
export interface ProductDetailSerializer {
  readonly category: any;
  readonly brand: any;
  readonly images: any;
  readonly currentPrice: any;
  readonly isOnSale: any;
  readonly discountPercentage: any;
  isInStock: any;
  categoryId: any;
  brandId?: any | null;
}


/**
 * Generated from ProductCreateUpdateSerializer serializer
 */
export interface ProductCreateUpdateSerializer {
  images?: any;
}


/**
 * Generated from ProductSearchSerializer serializer
 */
export interface ProductSearchSerializer {
  /** Search query */ query?: any;
  /** Category ID */ category?: any;
  /** Brand ID */ brand?: any;
  /** Minimum price */ minPrice?: any;
  /** Maximum price */ maxPrice?: any;
  /** Show only in-stock products */ inStockOnly: any;
  /** Show only featured products */ featuredOnly: any;
  /** Show only products on sale */ onSaleOnly: any;
  /** Product status */ status: any;
}

