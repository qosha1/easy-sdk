---
sidebar_position: 4
---

# Reviews API

The Reviews API provides endpoints for managing product reviews, ratings, and customer feedback.

## Overview

The reviews module includes:

- **Reviews** - Product reviews and ratings from customers
- **Review Responses** - Store owner responses to reviews
- **Review Helpful Votes** - Community feedback on review usefulness
- **Product Ratings** - Aggregated rating statistics per product

## Review Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reviews/` | List reviews |
| POST | `/api/reviews/` | Create new review |
| GET | `/api/reviews/{id}/` | Get review details |
| PUT | `/api/reviews/{id}/` | Update review |
| DELETE | `/api/reviews/{id}/` | Delete review |
| GET | `/api/reviews/my_reviews/` | Get current user's reviews |
| GET | `/api/reviews/pending_approval/` | Get pending reviews (admin) |
| POST | `/api/reviews/{id}/mark_helpful/` | Mark review as helpful |
| DELETE | `/api/reviews/{id}/unmark_helpful/` | Remove helpful mark |
| POST | `/api/reviews/{id}/respond/` | Add response to review (admin) |
| PATCH | `/api/reviews/{id}/approve/` | Approve review (admin) |
| PATCH | `/api/reviews/{id}/reject/` | Reject review (admin) |

## Review Helpful Votes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/review-helpful/` | List user's helpful votes |
| POST | `/api/review-helpful/` | Mark review as helpful |
| GET | `/api/review-helpful/{id}/` | Get helpful vote details |
| DELETE | `/api/review-helpful/{id}/` | Remove helpful vote |

## Review Responses

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/review-responses/` | List review responses |
| POST | `/api/review-responses/` | Create response (admin) |
| GET | `/api/review-responses/{id}/` | Get response details |
| PUT | `/api/review-responses/{id}/` | Update response (admin) |
| DELETE | `/api/review-responses/{id}/` | Delete response (admin) |

## Product Ratings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/product-ratings/` | List product rating stats |
| GET | `/api/product-ratings/{id}/` | Get rating stats for product |
| GET | `/api/product-ratings/top_rated/` | Get top-rated products |
| POST | `/api/product-ratings/{id}/refresh_stats/` | Refresh stats (admin) |

## Data Models

import DynamicTypeLoader from '@site/src/components/DynamicTypeLoader';

<DynamicTypeLoader 
  appName="reviews"
  title="Reviews App Data Models"
  showAllVariants={false}
/>

### Model Summary

The Reviews app includes the following serializers:
- **ReviewSerializer**: 2 fields
- **ReviewListSerializer**: 1 fields
- **ReviewResponseSerializer**: 1 fields  
- **ReviewHelpfulSerializer**: 1 fields
- **ProductRatingSerializer**: 2 fields
- **ReviewCreateSerializer**: 0 fields

### 🎯 Why Multiple Languages & Naming Conventions?

Different development environments have different conventions:

- **Frontend Teams**: Often prefer `camelCase` properties for JavaScript/TypeScript
- **Backend Teams**: May prefer `snake_case` to match Python/Django conventions  
- **Mobile Teams**: iOS uses `PascalCase`, Android varies by language
- **Integration Teams**: Need to match existing codebases and style guides

Easy-SDK generates **all variants automatically** so every team can use their preferred style without manual conversion.

## Review Creation Flow

### Submit a Review

```bash
POST /api/reviews/
Content-Type: application/json
Authorization: Token your-token-here

{
  "product": 1,
  "order": 5,  // Optional - links to purchase order
  "rating": 5,
  "title": "Amazing product!",
  "comment": "This product exceeded my expectations. Great quality and fast shipping."
}
```

### Mark Review as Helpful

```bash
POST /api/reviews/12/mark_helpful/
Authorization: Token your-token-here
```

### Admin Response to Review

```bash
POST /api/reviews/12/respond/
Content-Type: application/json
Authorization: Token admin-token-here

{
  "response_text": "Thank you for your feedback! We're glad you enjoyed the product."
}
```

## Filtering and Search

### Query Parameters

- `product` - Filter reviews by product ID
- `user` - Filter reviews by user ID (admin only)
- `rating` - Filter by specific rating (1-5)
- `is_approved` - Filter by approval status (admin)
- `is_verified_purchase` - Filter verified purchase reviews

### Examples

```bash
# Get all 5-star reviews for a product
GET /api/reviews/?product=1&rating=5

# Get pending approval reviews (admin)
GET /api/reviews/pending_approval/

# Get top-rated products with at least 10 reviews
GET /api/product-ratings/top_rated/?min_reviews=10
```

## Review Moderation

### Review States

- **Draft** - Review created but not yet approved
- **Approved** - Review is visible to public
- **Rejected** - Review was rejected by moderator

### Approval Workflow

1. Customer submits review
2. Review starts as `is_approved=True` by default (auto-approval)
3. Admin can manually approve/reject reviews
4. Rejected reviews are hidden from public view
5. Product rating stats update automatically

### Admin Actions

```bash
# Approve a review
PATCH /api/reviews/12/approve/
Authorization: Token admin-token-here

# Reject a review
PATCH /api/reviews/12/reject/
Authorization: Token admin-token-here
```

## Permissions

- **Public**: View approved reviews and ratings
- **Authenticated**: Create reviews, mark helpful, view own reviews
- **Review Owner**: Update/delete own reviews
- **Staff/Admin**: Approve/reject reviews, respond to reviews, access all reviews

## Validation Rules

- Users can only review products once
- Ratings must be between 1-5 stars
- Review title and comment are required
- Users cannot mark their own reviews as helpful
- Verified purchase badge appears for reviews linked to orders