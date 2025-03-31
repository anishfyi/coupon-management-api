# Coupon Management API Engineering Document

## 1. System Overview

This document outlines the architecture and implementation details for a RESTful API to manage and apply different types of discount coupons for an e-commerce platform. The system will support:

- Cart-wide discounts
- Product-specific discounts
- Buy X Get Y (BxGy) deals with repetition limits

### 1.1 Technology Stack

- **Backend Framework**: Django with Django REST Framework
- **Database**: SQLite (for simplicity, can be migrated to other databases if needed)
- **API Documentation**: Django REST Swagger/OpenAPI

## 2. Data Models

### 2.1 Coupon Model
```python
class Coupon:
    id: int  # Primary key
    type: str  # "cart-wise", "product-wise", "bxgy"
    is_active: bool  # Whether the coupon is currently active
    created_at: datetime
    updated_at: datetime
    expires_at: datetime  # Optional expiration date
```

### 2.2 Coupon Details Models
```python
class CartWiseCoupon:
    coupon_id: int  # Foreign key to Coupon
    threshold: decimal  # Minimum cart value for coupon to apply
    discount_percentage: decimal  # Percentage discount
```

```python
class ProductWiseCoupon:
    coupon_id: int  # Foreign key to Coupon
    product_id: int  # Product to which discount applies
    discount_percentage: decimal  # Percentage discount
```

```python
class BxGyCouponBuyProduct:
    coupon_id: int  # Foreign key to Coupon
    product_id: int  # Product in the "buy" category
    quantity: int  # Quantity to buy
```

```python
class BxGyCouponGetProduct:
    coupon_id: int  # Foreign key to Coupon
    product_id: int  # Product in the "get" category
    quantity: int  # Quantity to get free
```

```python
class BxGyCoupon:
    coupon_id: int  # Foreign key to Coupon
    repetition_limit: int  # Number of times coupon can be applied
```

### 2.3 Cart and Product Models (For API interaction)
```python
class CartItem:
    product_id: int
    quantity: int
    price: decimal
```

```python
class Cart:
    items: List[CartItem]
```

## 3. API Endpoints

### 3.1 Coupon Management
- `POST /coupons`: Create a new coupon
- `GET /coupons`: Retrieve all coupons
- `GET /coupons/{id}`: Retrieve a specific coupon by ID
- `PUT /coupons/{id}`: Update a specific coupon by ID
- `DELETE /coupons/{id}`: Delete a specific coupon by ID

### 3.2 Coupon Application
- `POST /applicable-coupons`: Fetch all applicable coupons for a given cart
- `POST /apply-coupon/{id}`: Apply a specific coupon to the cart

## 4. Business Logic

### 4.1 Coupon Applicability
- **Cart-wise**: Check if cart total exceeds threshold
- **Product-wise**: Check if specific product exists in cart
- **BxGy**: Check if required quantity of "buy" products exists in cart

### 4.2 Discount Calculation
- **Cart-wise**: Apply percentage discount to total cart value
- **Product-wise**: Apply percentage discount to specific product
- **BxGy**: Mark specific "get" products as free based on quantity of "buy" products

### 4.3 Edge Cases
1. Multiple applicable coupons
2. Coupon stacking (whether allowed or not)
3. Partial application of BxGy coupons
4. Handling of expired coupons
5. Product quantity changes after coupon application
6. Invalid coupon IDs or types

## 5. Implementation Approach

### 5.1 Application Structure
```
coupon_api/
├── coupons/
│   ├── models.py  # Coupon models
│   ├── serializers.py  # Request/response serializers
│   ├── views.py  # API endpoints
│   ├── coupon_logics/  # Coupon business logic
│   │   ├── cart_wise.py
│   │   ├── product_wise.py
│   │   ├── bxgy.py
├── api/  # API configuration
├── tests/  # Unit tests
└── manage.py
```

### 5.2 Implementation Strategy
1. Define and implement data models
2. Implement CRUD API endpoints for coupon management
3. Implement coupon applicability logic for each type
4. Implement discount calculation logic for each type
5. Implement API endpoints for coupon application
6. Add validation and error handling
7. Add unit tests
8. Document API and limitations

## 6. Testing Strategy
1. Unit tests for each coupon type logic
2. Integration tests for API endpoints
3. Edge case testing

## 7. Limitations and Assumptions

### 7.1 Limitations
- No user authentication/authorization
- No product database integration (products are referenced by ID only)
- In-memory cart handling
- Limited error handling

### 7.2 Assumptions
- Product IDs are valid and exist in an external system
- Cart items include accurate product information
- Coupons cannot be combined (only one coupon per cart)
- Percentage discounts are applied to the original price
- BxGy discounts are applied to the lowest-priced eligible products

## 8. Future Improvements
1. Add user authentication/authorization
2. Integrate with product database
3. Support coupon stacking with priority rules
4. Add more complex coupon types
5. Add analytics for coupon usage
6. Implement caching for better performance
7. Add webhooks for coupon events 