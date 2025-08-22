/**
 * Generated API Types
 * Common API types and utilities
 * 
 * This file was automatically generated. Do not edit manually.
 */


/**
 * Standard Django REST framework paginated response
 */
export interface PaginatedResponse {
  results: T[][];
  count: number;
  next: string | null;
  previous: string | null;
}


/**
 * API error response structure
 */
export interface ApiError {
  detail?: string;
  nonFieldErrors?: string[][];
}


/**
 * Common utility type: Nullable
 */
export type Nullable<T> = T | null;

/**
 * Common utility type: Optional
 */
export type Optional<T> = T | undefined;

/**
 * Common utility type: Partial
 */
export type Partial<T> = Partial<T>;

/**
 * Common utility type: ApiResponse
 */
export type ApiResponse<T> = { data: T; message?: string; success: boolean };

/**
 * Supported HTTP methods
 */
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

