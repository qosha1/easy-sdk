---
sidebar_position: 2
---

# Users API

The Users API provides endpoints for user management, authentication, profiles, addresses, and wishlists.

## Overview

The users module includes:

- **Authentication** - Login, registration, token management
- **User Management** - User profiles and account settings
- **Addresses** - Shipping and billing address management
- **Wishlists** - Product wishlist functionality

## Authentication Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user account |
| POST | `/api/auth/login/` | Authenticate user and get token |
| POST | `/api/auth/logout/` | Logout and invalidate token |
| GET | `/api/auth/profile/` | Get current user profile |
| POST | `/api/auth/refresh-token/` | Refresh authentication token |

## User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/` | List users (staff only) |
| POST | `/api/users/` | Create user (registration) |
| GET | `/api/users/{id}/` | Get user details |
| PUT | `/api/users/{id}/` | Update user |
| DELETE | `/api/users/{id}/` | Delete user |
| GET | `/api/users/me/` | Get current user info |
| GET | `/api/users/profile/` | Get/update user profile |
| PUT | `/api/users/profile/` | Update user profile |
| PATCH | `/api/users/profile/` | Partial profile update |
| POST | `/api/users/change_password/` | Change user password |

## Address Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/addresses/` | List user addresses |
| POST | `/api/addresses/` | Create new address |
| GET | `/api/addresses/{id}/` | Get address details |
| PUT | `/api/addresses/{id}/` | Update address |
| DELETE | `/api/addresses/{id}/` | Delete address |
| GET | `/api/addresses/shipping/` | Get shipping addresses |
| GET | `/api/addresses/billing/` | Get billing addresses |
| GET | `/api/addresses/default_shipping/` | Get default shipping address |
| GET | `/api/addresses/default_billing/` | Get default billing address |
| PATCH | `/api/addresses/{id}/set_default/` | Set address as default |

## Wishlist Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/wishlists/` | Get user's wishlist |
| GET | `/api/wishlists/{id}/` | Get wishlist details |
| GET | `/api/wishlist-items/` | List wishlist items |
| POST | `/api/wishlist-items/` | Add item to wishlist |
| DELETE | `/api/wishlist-items/{id}/` | Remove item from wishlist |
| POST | `/api/wishlist-items/toggle/` | Toggle item in wishlist |
| DELETE | `/api/wishlist-items/clear/` | Clear all wishlist items |
| POST | `/api/wishlist-items/add_multiple/` | Add multiple items |

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