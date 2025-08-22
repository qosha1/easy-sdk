import { PaginatedResponse, ApiError, Nullable, Optional } from './common';

/**
 * Generated API Types
 * Generated types for users app
 * 
 * This file was automatically generated. Do not edit manually.
 */


/**
 * Generated from UserSerializer serializer
 */
export interface UserSerializer {
  fullName: any;
}


/**
 * Generated from UserProfileSerializer serializer
 */
export interface UserProfileSerializer {
  readonly user: any;
  readonly fullName: any;
}


/**
 * Generated from AddressSerializer serializer
 */
export interface AddressSerializer {
  readonly fullName: any;
  readonly formattedAddress: any;
}


/**
 * Generated from WishlistItemSerializer serializer
 */
export interface WishlistItemSerializer {
  readonly productName: any;
  readonly productPrice: any;
  productImage: any;
  isInStock: any;
}


/**
 * Generated from WishlistSerializer serializer
 */
export interface WishlistSerializer {
  readonly items: any;
  totalItems: any;
}


/**
 * Generated from UserRegistrationSerializer serializer
 */
export interface UserRegistrationSerializer {
  password: any;
  passwordConfirm: any;
}


/**
 * Generated from UserUpdateSerializer serializer
 */
export interface UserUpdateSerializer {
  profile?: any;
}


/**
 * Generated from PasswordChangeSerializer serializer
 */
export interface PasswordChangeSerializer {
  oldPassword: any;
  newPassword: any;
  newPasswordConfirm: any;
}

