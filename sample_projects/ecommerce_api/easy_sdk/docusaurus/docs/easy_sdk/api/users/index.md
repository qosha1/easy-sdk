---
sidebar_position: 2
---

# Users API

import SwaggerApiDocs from '@site/src/components/SwaggerApiDocs';

<SwaggerApiDocs 
  appName="users"
  title="Users API"
  description="The Users API provides endpoints for user management, authentication, profiles, addresses, and wishlists. This includes login/registration, user profiles, shipping/billing addresses, and wishlist functionality."
  serializers={[
    {
      name: 'UserSerializer',
      fields: {
        id: { type: 'IntegerField', required: false, read_only: true, help_text: 'Unique user identifier' },
        username: { type: 'CharField', required: true, max_length: 150, help_text: 'Username for authentication' },
        email: { type: 'EmailField', required: true, help_text: 'User email address' },
        first_name: { type: 'CharField', required: false, max_length: 150, help_text: 'User first name' },
        last_name: { type: 'CharField', required: false, max_length: 150, help_text: 'User last name' },
        is_active: { type: 'BooleanField', required: false, read_only: true, help_text: 'Whether user account is active' },
        date_joined: { type: 'DateTimeField', required: false, read_only: true, help_text: 'Account creation timestamp' }
      },
      docstring: 'User account information and details'
    },
    {
      name: 'UserRegistrationSerializer', 
      fields: {
        username: { type: 'CharField', required: true, max_length: 150, help_text: 'Desired username' },
        email: { type: 'EmailField', required: true, help_text: 'Email address for account' },
        first_name: { type: 'CharField', required: false, max_length: 150, help_text: 'First name' },
        last_name: { type: 'CharField', required: false, max_length: 150, help_text: 'Last name' },
        password: { type: 'CharField', required: true, write_only: true, help_text: 'Account password' },
        password_confirm: { type: 'CharField', required: true, write_only: true, help_text: 'Confirm password' }
      },
      docstring: 'User registration data'
    },
    {
      name: 'AddressSerializer',
      fields: {
        id: { type: 'IntegerField', required: false, read_only: true, help_text: 'Address ID' },
        user: { type: 'ForeignKey', required: false, read_only: true, help_text: 'User this address belongs to' },
        first_name: { type: 'CharField', required: true, max_length: 100, help_text: 'First name' },
        last_name: { type: 'CharField', required: true, max_length: 100, help_text: 'Last name' },
        address_line_1: { type: 'CharField', required: true, max_length: 255, help_text: 'Address line 1' },
        address_line_2: { type: 'CharField', required: false, max_length: 255, help_text: 'Address line 2' },
        city: { type: 'CharField', required: true, max_length: 100, help_text: 'City' },
        state_province: { type: 'CharField', required: false, max_length: 100, help_text: 'State or province' },
        postal_code: { type: 'CharField', required: true, max_length: 20, help_text: 'Postal/ZIP code' },
        country: { type: 'CharField', required: true, max_length: 2, help_text: 'ISO country code' },
        is_default_shipping: { type: 'BooleanField', required: false, help_text: 'Default shipping address' },
        is_default_billing: { type: 'BooleanField', required: false, help_text: 'Default billing address' }
      },
      docstring: 'User shipping and billing address information'
    },
    {
      name: 'WishlistItemSerializer',
      fields: {
        id: { type: 'IntegerField', required: false, read_only: true, help_text: 'Wishlist item ID' },
        product: { type: 'ForeignKey', required: true, help_text: 'Product to add to wishlist' },
        added_date: { type: 'DateTimeField', required: false, read_only: true, help_text: 'Date added to wishlist' },
        notes: { type: 'TextField', required: false, help_text: 'Optional notes about this item' }
      },
      docstring: 'Item in user wishlist'
    }
  ]}
  endpoints={[
    // Authentication endpoints
    { method: 'POST', path: '/api/auth/register/', description: 'Register new user account', serializer_class: 'UserRegistrationSerializer', tags: ['Authentication'] },
    { method: 'POST', path: '/api/auth/login/', description: 'Authenticate user and get token', tags: ['Authentication'] },
    { method: 'POST', path: '/api/auth/logout/', description: 'Logout and invalidate token', tags: ['Authentication'] },
    { method: 'GET', path: '/api/auth/profile/', description: 'Get current user profile', serializer_class: 'UserSerializer', tags: ['Authentication'] },
    { method: 'POST', path: '/api/auth/refresh-token/', description: 'Refresh authentication token', tags: ['Authentication'] },
    
    // User management
    { method: 'GET', path: '/api/users/', description: 'List users (staff only)', serializer_class: 'UserSerializer', tags: ['User Management'] },
    { method: 'POST', path: '/api/users/', description: 'Create user (registration)', serializer_class: 'UserRegistrationSerializer', tags: ['User Management'] },
    { method: 'GET', path: '/api/users/{id}/', description: 'Get user details', serializer_class: 'UserSerializer', tags: ['User Management'] },
    { method: 'PUT', path: '/api/users/{id}/', description: 'Update user', serializer_class: 'UserSerializer', tags: ['User Management'] },
    { method: 'DELETE', path: '/api/users/{id}/', description: 'Delete user', tags: ['User Management'] },
    { method: 'GET', path: '/api/users/me/', description: 'Get current user info', serializer_class: 'UserSerializer', tags: ['User Management'] },
    { method: 'POST', path: '/api/users/change_password/', description: 'Change user password', tags: ['User Management'] },
    
    // Address management
    { method: 'GET', path: '/api/addresses/', description: 'List user addresses', serializer_class: 'AddressSerializer', tags: ['Address Management'] },
    { method: 'POST', path: '/api/addresses/', description: 'Create new address', serializer_class: 'AddressSerializer', tags: ['Address Management'] },
    { method: 'GET', path: '/api/addresses/{id}/', description: 'Get address details', serializer_class: 'AddressSerializer', tags: ['Address Management'] },
    { method: 'PUT', path: '/api/addresses/{id}/', description: 'Update address', serializer_class: 'AddressSerializer', tags: ['Address Management'] },
    { method: 'DELETE', path: '/api/addresses/{id}/', description: 'Delete address', tags: ['Address Management'] },
    { method: 'GET', path: '/api/addresses/shipping/', description: 'Get shipping addresses', serializer_class: 'AddressSerializer', tags: ['Address Management'] },
    { method: 'GET', path: '/api/addresses/billing/', description: 'Get billing addresses', serializer_class: 'AddressSerializer', tags: ['Address Management'] },
    { method: 'PATCH', path: '/api/addresses/{id}/set_default/', description: 'Set address as default', tags: ['Address Management'] },
    
    // Wishlist management
    { method: 'GET', path: '/api/wishlists/', description: 'Get user wishlist', tags: ['Wishlist Management'] },
    { method: 'GET', path: '/api/wishlist-items/', description: 'List wishlist items', serializer_class: 'WishlistItemSerializer', tags: ['Wishlist Management'] },
    { method: 'POST', path: '/api/wishlist-items/', description: 'Add item to wishlist', serializer_class: 'WishlistItemSerializer', tags: ['Wishlist Management'] },
    { method: 'DELETE', path: '/api/wishlist-items/{id}/', description: 'Remove item from wishlist', tags: ['Wishlist Management'] },
    { method: 'POST', path: '/api/wishlist-items/toggle/', description: 'Toggle item in wishlist', tags: ['Wishlist Management'] },
    { method: 'DELETE', path: '/api/wishlist-items/clear/', description: 'Clear all wishlist items', tags: ['Wishlist Management'] }
  ]}
/>

## Quick Examples

### Register a New User

```bash
POST /api/auth/register/
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com", 
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepassword123",
  "password_confirm": "securepassword123"
}
```

### Add Item to Wishlist

```bash
POST /api/wishlist-items/
Authorization: Bearer your-token-here
Content-Type: application/json

{
  "product": 1,
  "notes": "Want to buy this for my birthday"
}
```

## Data Models

import DynamicTypeLoader from '@site/src/components/DynamicTypeLoader';

<DynamicTypeLoader 
  appName="users"
  title="Users App Data Models"
  showAllVariants={false}
/>

### Model Summary

The Users app includes the following serializers:
- **UserSerializer**: 1 fields
- **UserProfileSerializer**: 2 fields
- **AddressSerializer**: 2 fields
- **WishlistItemSerializer**: 4 fields
- **WishlistSerializer**: 2 fields
- **UserRegistrationSerializer**: 2 fields
- **UserUpdateSerializer**: 1 fields
- **PasswordChangeSerializer**: 3 fields

### 🎯 Why Multiple Languages & Naming Conventions?

Different development environments have different conventions:

- **Frontend Teams**: Often prefer `camelCase` properties for JavaScript/TypeScript
- **Backend Teams**: May prefer `snake_case` to match Python/Django conventions  
- **Mobile Teams**: iOS uses `PascalCase`, Android varies by language
- **Integration Teams**: Need to match existing codebases and style guides

Easy-SDK generates **all variants automatically** so every team can use their preferred style without manual conversion.

## Authentication Flow

### Registration

```bash
POST /api/auth/register/
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepassword123",
  "password_confirm": "securepassword123"
}
```

### Login

```bash
POST /api/auth/login/
Content-Type: application/json

{
  "username": "newuser",
  "password": "securepassword123"
}

# Response
{
  "message": "Login successful",
  "user": { /* user data */ },
  "token": "abc123tokendef456"
}
```

### Using Token

```bash
GET /api/users/profile/
Authorization: Token abc123tokendef456
```

## Permissions

- **Public**: Registration, login
- **Authenticated**: Profile management, addresses, wishlist
- **Owner Only**: Users can only access/modify their own data
- **Staff**: Can access all user data for admin purposes