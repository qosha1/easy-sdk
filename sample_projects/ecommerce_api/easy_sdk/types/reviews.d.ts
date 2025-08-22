import { PaginatedResponse, ApiError, Nullable, Optional } from './common';

/**
 * Generated API Types
 * Generated types for reviews app
 * 
 * This file was automatically generated. Do not edit manually.
 */


/**
 * Generated from ReviewSerializer serializer
 */
export interface ReviewSerializer {
  readonly userName: any;
  readonly productName: any;
  isHelpfulToUser: any;
  response: any;
}


/**
 * Generated from ReviewListSerializer serializer
 */
export interface ReviewListSerializer {
  readonly userName: any;
}


/**
 * Generated from ReviewResponseSerializer serializer
 */
export interface ReviewResponseSerializer {
  readonly responderName: any;
}


/**
 * Generated from ReviewHelpfulSerializer serializer
 */
export interface ReviewHelpfulSerializer {
  readonly userName: any;
}


/**
 * Generated from ProductRatingSerializer serializer
 */
export interface ProductRatingSerializer {
  readonly productName: any;
  readonly ratingDistribution: any;
}


/**
 * Generated from ReviewCreateSerializer serializer
 */
export interface ReviewCreateSerializer {
}


/**
 * Generated from ReviewUpdateSerializer serializer
 */
export interface ReviewUpdateSerializer {
}


/**
 * Generated from ReviewModerationSerializer serializer
 */
export interface ReviewModerationSerializer {
}

