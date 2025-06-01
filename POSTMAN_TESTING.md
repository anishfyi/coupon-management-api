# Coupon Management API Testing Guide

This document provides comprehensive instructions for testing the Coupon Management API using Postman, including environment setup, testing workflows, and best practices.

## Table of Contents
1. [Setup](#setup)
2. [Environment Configuration](#environment-configuration)
3. [Testing Workflows](#testing-workflows)
4. [API Endpoints](#api-endpoints)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Setup

1. **Install Postman**
   - Download and install Postman from [postman.com](https://www.postman.com/downloads/)
   - Create a free account to save your collections and environments

2. **Start the Development Server**
   ```bash
   python manage.py runserver
   ```

3. **Import the Postman Collection**
   - Download the collection JSON file from the repository
   - In Postman, click "Import" → "File" → Select the collection file
   - The collection will be imported with all endpoints pre-configured

## Environment Configuration

1. **Create a New Environment**
   - Click "Environments" → "Create Environment"
   - Name it "Coupon API Local"
   - Add the following variables:
     ```
     base_url: http://127.0.0.1:8000
     api_version: v1
     ```

2. **Environment Variables Usage**
   - Use `{{base_url}}/api/` in your requests
   - This makes it easy to switch between environments (local, staging, production)

## Testing Workflows

### 1. Basic Coupon Management Flow
1. Create a new coupon (POST /api/coupons/)
2. Verify the coupon was created (GET /api/coupons/{{coupon_id}}/)
3. Update the coupon (PUT /api/coupons/{{coupon_id}}/)
4. Delete the coupon (DELETE /api/coupons/<coupon_id>/)

### 2. Coupon Application Flow
1. Create multiple coupons of different types
2. Get applicable coupons for a cart (POST /api/applicable-coupons/)
3. Apply a specific coupon (POST /api/apply-coupon/<coupon_id>/)
4. Verify the discount calculations

### 3. Edge Cases to Test
1. Expired coupons
2. Inactive coupons
3. Invalid coupon codes
4. Cart totals below threshold
5. Product quantities exceeding limits
6. Multiple applicable coupons

## Authentication

The current implementation doesn't require authentication for API endpoints.

## API Endpoints

### 1. Coupon Management

#### 1.1. Create a Coupon (POST /api/coupons/)

**Request:**
- Method: POST
- URL: `http://127.0.0.1:8000/api/coupons/`
- Headers:
  - Content-Type: application/json
- Body:

**Example 1: Cart-wise Coupon (Percentage Discount)**
```json
{
  "type": "cart-wise",
  "code": "CART10",
  "name": "10% Off on Orders Above $100",
  "description": "Get 10% off on your entire cart when you spend over $100",
  "is_active": true,
  "expires_at": "2025-12-31T23:59:59Z",
  "cart_wise_details": {
    "discount_type": "percentage",
    "threshold": 100.00,
    "discount_value": 10.00
  }
}
```

**Example 2: Product-wise Coupon**
```json
{
  "type": "product-wise",
  "code": "PROD20",
  "name": "20% Off on Product #1",
  "description": "Get 20% off on Product #1",
  "is_active": true,
  "product_wise_details": {
    "discount_type": "percentage",
    "product_id": 1,
    "discount_value": 20.00
  }
}
```

**Example 3: BxGy Coupon**
```json
{
  "type": "bxgy",
  "code": "B2G1FREE",
  "name": "Buy 2 Get 1 Free",
  "description": "Buy 2 of Product #1, get 1 of Product #3 free",
  "is_active": true,
  "bxgy_details": {
    "repetition_limit": 3,
    "buy_products": [
      {
        "product_id": 1,
        "quantity": 2
      }
    ],
    "get_products": [
      {
        "product_id": 3,
        "quantity": 1
      }
    ]
  }
}
```

#### 1.2. Get All Coupons (GET /api/coupons/)

**Request:**
- Method: GET
- URL: `http://127.0.0.1:8000/api/coupons/`

#### 1.3. Get Coupon by ID (GET /api/coupons/{{coupon_id}}/)

**Request:**
- Method: GET
- URL: `http://127.0.0.1:8000/api/coupons/{{coupon_id}}/`
  - Replace `coupon_id` with the UUID of the coupon

#### 1.4. Update Coupon (PUT /api/coupons/{{coupon_id}}/)

**Request:**
- Method: PUT
- URL: `http://127.0.0.1:8000/api/coupons/{{coupon_id}}/`
  - Replace `{{coupon_id}}` with the UUID of the coupon
- Headers:
  - Content-Type: application/json
- Body: Same format as create coupon, but with fields you want to update

#### 1.5. Delete Coupon (DELETE /api/coupons/<coupon_id>/)

**Request:**
- Method: DELETE
- URL: `http://127.0.0.1:8000/api/coupons/<coupon_id>/`
  - Replace `<coupon_id>` with the UUID of the coupon

### 2. Coupon Application

#### 2.1. Get Applicable Coupons (POST /api/applicable-coupons/)

**Request:**
- Method: POST
- URL: `http://127.0.0.1:8000/api/applicable-coupons/`
- Headers:
  - Content-Type: application/json
- Body:

```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 3,
      "price": 50.00
    },
    {
      "product_id": 2,
      "quantity": 2,
      "price": 30.00
    },
    {
      "product_id": 3,
      "quantity": 1,
      "price": 25.00
    }
  ]
}
```

**Response:**
```json
{
  "applicable_coupons": [
    {
      "coupon_id": "a1b2c3d4-...",
      "type": "cart-wise",
      "name": "10% Off on Orders Above $100",
      "code": "CART10",
      "discount": 23.50
    },
    {
      "coupon_id": "e5f6g7h8-...",
      "type": "bxgy",
      "name": "Buy 2 Get 1 Free",
      "code": "B2G1FREE",
      "discount": 25.00
    }
  ]
}
```

#### 2.2. Apply Coupon (POST /api/apply-coupon/<coupon_id>/)

**Request:**
- Method: POST
- URL: `http://127.0.0.1:8000/api/apply-coupon/<coupon_id>/`
  - Replace `<coupon_id>` with the UUID of the coupon
- Headers:
  - Content-Type: application/json
- Body:

```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 3,
      "price": 50.00
    },
    {
      "product_id": 2,
      "quantity": 2,
      "price": 30.00
    },
    {
      "product_id": 3,
      "quantity": 1,
      "price": 25.00
    }
  ]
}
```

**Response (Cart-wise Coupon):**
```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 3,
      "price": 50.00,
      "total_discount": 0.00
    },
    {
      "product_id": 2,
      "quantity": 2,
      "price": 30.00,
      "total_discount": 0.00
    },
    {
      "product_id": 3,
      "quantity": 1,
      "price": 25.00,
      "total_discount": 0.00
    }
  ],
  "total_price": 235.00,
  "total_discount": 23.50,
  "final_price": 211.50
}
```

**Response (Product-wise Coupon):**
```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 3,
      "price": 50.00,
      "total_discount": 30.00
    },
    {
      "product_id": 2,
      "quantity": 2,
      "price": 30.00,
      "total_discount": 0.00
    },
    {
      "product_id": 3,
      "quantity": 1,
      "price": 25.00,
      "total_discount": 0.00
    }
  ],
  "total_price": 235.00,
  "total_discount": 30.00,
  "final_price": 205.00
}
```

**Response (BxGy Coupon):**
```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 3,
      "price": 50.00,
      "total_discount": 0.00
    },
    {
      "product_id": 2,
      "quantity": 2,
      "price": 30.00,
      "total_discount": 0.00
    },
    {
      "product_id": 3,
      "quantity": 1,
      "price": 25.00,
      "total_discount": 25.00
    }
  ],
  "total_price": 235.00,
  "total_discount": 25.00,
  "final_price": 210.00
}
```

## Testing Scenarios

### Scenario 1: Cart-wise Coupon Testing

1. Create a cart-wise coupon with a threshold of $100 and 10% discount
2. Test with a cart below the threshold (should not be applicable)
3. Test with a cart above the threshold (should apply 10% discount to total)

### Scenario 2: Product-wise Coupon Testing

1. Create a product-wise coupon with 20% off on Product #1
2. Test with a cart that doesn't contain Product #1 (should not be applicable)
3. Test with a cart containing Product #1 (should apply 20% discount to Product #1 only)

### Scenario 3: BxGy Coupon Testing

1. Create a BxGy coupon: Buy 2 of Product #1, get 1 of Product #3 free
2. Test with insufficient quantity of buy products (should not be applicable)
3. Test with sufficient buy products but no get products (should not be applicable)
4. Test with both sufficient buy and get products (should make the get product free)
5. Test with multiple repetitions (e.g., buy 6 get 3 free)

### Scenario 4: Expired Coupon Testing

1. Create a coupon with an expiration date in the past
2. Attempt to apply the coupon (should fail with an appropriate error message)

## Best Practices

1. **Request Organization**
   - Use folders in your collection to group related endpoints
   - Name your requests descriptively
   - Add request descriptions for complex endpoints

2. **Test Scripts**
   - Add test scripts to verify responses
   - Example test script for coupon creation:
   ```javascript
   pm.test("Status code is 201", function () {
       pm.response.to.have.status(201);
   });
   
   pm.test("Response has required fields", function () {
       const response = pm.response.json();
       pm.expect(response).to.have.property('id');
       pm.expect(response).to.have.property('code');
       pm.expect(response).to.have.property('type');
   });
   ```

3. **Variables and Dynamic Data**
   - Use collection variables for common values
   - Extract response values to variables for use in subsequent requests
   - Example: Extract coupon ID from create response:
   ```javascript
   const response = pm.response.json();
   pm.collectionVariables.set("coupon_id", response.id);
   ```

4. **Request Headers**
   - Always include `Content-Type: application/json`
   - Add custom headers if required by your implementation

## Troubleshooting

1. **Common Issues**
   - 404 Not Found: Verify the server is running and URL is correct
   - 400 Bad Request: Check request body format and required fields
   - 500 Server Error: Check server logs for detailed error messages

2. **Debugging Tips**
   - Use Postman Console (View → Show Postman Console)
   - Enable verbose logging in your Django settings
   - Check response headers for additional information

3. **Performance Testing**
   - Use Postman's Collection Runner for load testing
   - Monitor response times
   - Test with various payload sizes

### UUID Format:

When retrieving a specific coupon or applying a coupon, ensure the UUID format is correct. A valid UUID looks like: `123e4567-e89b-12d3-a456-426614174000`

## Advanced Testing

### Testing Category and Brand Discounts

Add `category` and `brand` fields to cart items to test category-wide and brand-wide discounts:

```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "price": 50.00,
      "category": "electronics",
      "brand": "samsung"
    }
  ]
}
```

### Testing Multiple Applicable Coupons

1. Create multiple coupons that could apply to the same cart
2. Use the applicable-coupons endpoint to see all possible discounts
3. Compare the results to verify the highest discount is shown first 