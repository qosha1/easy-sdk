/**
 * Common API Types
 * Generated for Django API
 */

/**
 * Common utility type: Nullable
 */
export type Nullable = T | null;

/**
 * Common utility type: Optional
 */
export type Optional = T | undefined;

/**
 * Common utility type: Partial
 */
export type Partial = Partial<T>;

/**
 * Common utility type: ApiResponse
 */
export type ApiResponse = { data: T; message?: string; success: boolean };

/**
 * Common utility type: PaginatedResponse
 */
export type PaginatedResponse = { results: T[]; count: number; next?: string; previous?: string };

/**
 * Common utility type: ValidationError
 */
export type ValidationError = { field?: string; message: string; code?: string };

/**
 * Standard Django REST framework paginated response
 */
export interface PaginatedResponse {
  results: T[];
  count: number;
  next: string | null;
  previous: string | null;
}

/**
 * API error response structure
 */
export interface ApiError {
  detail?: string;
  non_field_errors?: string[];
  [field: string]: string[] | string;
}

/**
 * Supported HTTP methods
 */
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
