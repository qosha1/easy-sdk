# E-commerce API Sample Project

This is a sample Django REST Framework project demonstrating an e-commerce API with comprehensive examples for Easy SDK documentation and SDK generation.

## 🚀 Quick Start

### Generate Documentation

```bash
# Generate interactive Docusaurus documentation
easy-sdk . --format docusaurus

# Generate Sphinx documentation
easy-sdk . --format sphinx
```

### Generate Client SDKs

```bash
# Generate Python SDK
easy-sdk . generate-sdk --language python --library-name "ecommerce_client"

# Generate TypeScript SDK  
easy-sdk . generate-sdk --language typescript --library-name "ecommerce-client"

# Generate both
easy-sdk . generate-sdk --language python --language typescript --library-name "ecommerce_api"
```

## 📚 API Structure

This sample project includes the following Django apps:

### **Users App**
- User registration and authentication
- User profiles and preferences
- User management endpoints

**Endpoints:**
- `GET /api/users/` - List users
- `POST /api/users/` - Create user
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user

### **Products App**
- Product catalog management
- Categories and product variations
- Inventory tracking

**Endpoints:**
- `GET /api/products/` - List products
- `POST /api/products/` - Create product  
- `GET /api/products/{id}/` - Get product details
- `PUT /api/products/{id}/` - Update product
- `DELETE /api/products/{id}/` - Delete product

### **Orders App**
- Order management and processing
- Order status tracking
- Payment integration

**Endpoints:**
- `GET /api/orders/` - List orders
- `POST /api/orders/` - Create order
- `GET /api/orders/{id}/` - Get order details
- `PUT /api/orders/{id}/` - Update order
- `DELETE /api/orders/{id}/` - Cancel order

### **Reviews App**
- Product reviews and ratings
- Review moderation
- Rating aggregation

**Endpoints:**
- `GET /api/reviews/` - List reviews
- `POST /api/reviews/` - Create review
- `GET /api/reviews/{id}/` - Get review details
- `PUT /api/reviews/{id}/` - Update review
- `DELETE /api/reviews/{id}/` - Delete review

## 🛠 SDK Usage Examples

### Generated Python SDK

After generating the Python SDK:

```python
import asyncio
from ecommerce_client import EcommerceApiClient

async def main():
    async with EcommerceApiClient(
        api_key="your-api-key",
        base_url="http://localhost:8000"
    ) as client:
        
        # Create a user
        user = await client.users.create_user({
            "email": "john@example.com",
            "username": "johnsmith",
            "first_name": "John",
            "last_name": "Smith"
        })
        
        # List products
        products = await client.products.list_products()
        
        # Create an order
        order = await client.orders.create_order({
            "user": user["id"],
            "items": [
                {"product": products[0]["id"], "quantity": 2}
            ]
        })
        
        # Add a review
        review = await client.reviews.create_review({
            "product": products[0]["id"],
            "user": user["id"],
            "rating": 5,
            "comment": "Great product!"
        })

asyncio.run(main())
```

### Generated TypeScript SDK

After generating the TypeScript SDK:

```typescript
import { EcommerceApiClient, User, Product, Order } from 'ecommerce-client';

const client = new EcommerceApiClient({
  apiKey: 'your-api-key',
  baseUrl: 'http://localhost:8000'
});

async function example() {
  // Create a user with full type safety
  const user: User = await client.users.createUser({
    email: 'jane@example.com',
    username: 'janesmith',
    firstName: 'Jane',
    lastName: 'Smith'
  });
  
  // List products with typed responses
  const products: Product[] = await client.products.listProducts({
    page: 1,
    pageSize: 10,
    category: 'electronics'
  });
  
  // Create an order
  const order: Order = await client.orders.createOrder({
    user: user.id,
    items: [
      { product: products[0].id, quantity: 2 }
    ]
  });
  
  console.log('Order created:', order.id);
}
```

## 📊 Generated Documentation Features

### Interactive Docusaurus Documentation

- 🧪 **Live API Testing** - Test endpoints directly in the browser
- 📊 **Schema Visualization** - Interactive object schema exploration  
- 🎨 **Modern UI** - Clean, Swagger-style interface
- 📝 **Auto-generated Examples** - Request/response examples for all endpoints
- 🔧 **Authentication Support** - Built-in token management for testing

### Traditional Sphinx Documentation

- 📚 **Comprehensive Reference** - Complete API documentation
- 🏗 **Organized Structure** - Documentation organized by Django apps
- 📖 **Detailed Descriptions** - Field-level documentation with validation rules
- 🔗 **Cross-references** - Linked references between models and endpoints

## 🤖 AI-Enhanced Features

Easy SDK can use AI to enhance the generated documentation and SDKs:

```bash
# Use OpenAI for enhanced analysis
export OPENAI_API_KEY=sk-your-key
easy-sdk . generate-sdk --language python --ai-provider openai --ai-model gpt-4

# Use Anthropic Claude
export ANTHROPIC_API_KEY=sk-ant-your-key  
easy-sdk . generate-sdk --language typescript --ai-provider anthropic --ai-model claude-3
```

**AI enhancements include:**
- Smart API structure analysis for optimal SDK organization
- Enhanced field descriptions and documentation
- Intelligent error handling patterns
- Architecture recommendations for complex APIs

## 🔧 Configuration

Create `.easy-sdk.toml` for custom configuration:

```toml
[project]
name = "E-commerce API"
version = "1.0.0"

[generation]
documentation_format = "docusaurus"
generate_multiple_languages = true
additional_languages = ["python", "typescript"]

[output]
base_output_dir = "./generated"

[ai]
provider = "openai"
model = "gpt-4"

[apps]
include_apps = ["users", "products", "orders", "reviews"]
```

## 🚦 Development Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Create sample data:**
   ```bash
   python manage.py create_sample_data
   ```

4. **Start the server:**
   ```bash
   python manage.py runserver
   ```

5. **Generate documentation:**
   ```bash
   easy-sdk . --format docusaurus
   ```

## 📁 Project Structure

```
ecommerce_api/
├── manage.py
├── requirements.txt
├── .easy-sdk.toml
├── ecommerce_api/         # Main Django project
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── users/                 # User management app
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── products/              # Product catalog app
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── orders/                # Order management app
│   └── ...
├── reviews/               # Review system app
│   └── ...
└── generated/             # Generated documentation & SDKs
    ├── docs/              # Documentation
    ├── sdk_python/        # Python SDK
    └── sdk_typescript/    # TypeScript SDK
```

## 🎯 Use Cases

This sample demonstrates Easy SDK's capabilities for:

- **E-commerce platforms** - Product catalogs, order management, user accounts
- **Content management** - Reviews, ratings, user-generated content
- **Multi-app APIs** - Complex Django projects with multiple interconnected apps
- **Authentication patterns** - Token-based auth, user permissions
- **CRUD operations** - Complete create, read, update, delete functionality

## 📈 Performance

The generated SDKs include production-ready features:

- **Connection pooling** - Efficient HTTP connection management
- **Automatic retries** - Exponential backoff for failed requests
- **Rate limiting** - Built-in rate limit handling
- **Error handling** - Comprehensive exception hierarchy
- **Type safety** - Full type checking in TypeScript, type hints in Python

---

This sample project showcases the full power of Easy SDK for generating documentation and client libraries from Django REST Framework APIs.