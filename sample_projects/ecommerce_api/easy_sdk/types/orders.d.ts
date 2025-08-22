import { PaginatedResponse, ApiError, Nullable, Optional } from './common';

/**
 * Generated API Types
 * Generated types for orders app
 * 
 * This file was automatically generated. Do not edit manually.
 */


/**
 * Generated from CartItemSerializer serializer
 */
export interface CartItemSerializer {
  readonly productName: any;
  readonly productSku: any;
  readonly unitPrice: any;
  readonly totalPrice: any;
  productImage: any;
  isInStock: any;
}


/**
 * Generated from CartSerializer serializer
 */
export interface CartSerializer {
  readonly items: any;
  readonly totalItems: any;
  readonly totalPrice: any;
}


/**
 * Generated from OrderItemSerializer serializer
 */
export interface OrderItemSerializer {
}


/**
 * Generated from OrderListSerializer serializer
 */
export interface OrderListSerializer {
  readonly totalItems: any;
  customerName: any;
}


/**
 * Generated from OrderDetailSerializer serializer
 */
export interface OrderDetailSerializer {
  readonly items: any;
  readonly totalItems: any;
  customerName: any;
}


/**
 * Generated from OrderCreateSerializer serializer
 */
export interface OrderCreateSerializer {
  items: any;
}


/**
 * Generated from OrderUpdateSerializer serializer
 */
export interface OrderUpdateSerializer {
}


/**
 * Generated from PaymentSerializer serializer
 */
export interface PaymentSerializer {
  readonly orderNumber: any;
}


/**
 * Generated from CartToOrderSerializer serializer
 */
export interface CartToOrderSerializer {
  /** Shipping address as JSON object */ shippingAddress: any;
  /** Billing address as JSON object */ billingAddress: any;
  /** Optional customer notes */ customerNotes?: any;
  /** Payment method for the order */ paymentMethod: any;
}

