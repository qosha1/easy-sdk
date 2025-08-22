---
sidebar_position: 1
---

# Django API API Documentation

Auto-generated API documentation

**Version:** 1.0.0

## Overview

This documentation provides comprehensive information about the Django API API endpoints, serializers, and data models.

## Available Apps

- [Products](./api/products) - products API documentation
- [Users](./api/users) - users API documentation
- [Orders](./api/orders) - orders API documentation
- [Reviews](./api/reviews) - reviews API documentation


## Getting Started

### Authentication

Most API endpoints require authentication. Include your API token in the Authorization header:

```http
Authorization: Bearer YOUR_API_TOKEN
```

### Response Format

All API responses follow a consistent JSON format:

```json
{
  "data": {},
  "message": "Success message",
  "success": true
}
```

### Error Handling

Error responses include detailed information:

```json
{
  "error": {
    "detail": "Error description",
    "code": "ERROR_CODE"
  },
  "success": false
}
```

## SDKs and Libraries

### JavaScript/TypeScript

```bash
npm install axios
```

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  }
});
```

### Python

```bash
pip install requests
```

```python
import requests

BASE_URL = 'http://localhost:8000/api'
headers = {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
}
```

:::note Generated Documentation

This documentation was automatically generated from Django code analysis using [easy-sdk](https://github.com/your-org/easy-sdk).

:::
