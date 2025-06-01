# Coupon Management API

A RESTful API to manage and apply different types of discount coupons for an e-commerce platform.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Setup and Installation](#setup-and-installation)
- [API Endpoints](#api-endpoints)
- [Coupon Cases](#coupon-cases)
  - [Implemented Cases](#implemented-cases)
  - [Non-implemented Cases](#non-implemented-cases)
- [Limitations and Assumptions](#limitations-and-assumptions)
- [Future Improvements](#future-improvements)

## Overview

This API allows an e-commerce platform to manage and apply various discount coupons including cart-wide discounts, product-specific discounts, and "Buy X Get Y" (BxGy) deals with repetition limits.

## Features

- Create, read, update, and delete coupons
- Check applicable coupons for a given cart
- Apply a specific coupon to a cart and calculate the discounted prices
- Support for multiple coupon types
- Expiration dates for coupons

## Technology Stack

- **Backend Framework**: Django with Django REST Framework
- **Database**: SQLite
- **Documentation**: OpenAPI/Swagger

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/coupon-management-api.git
cd coupon-management-api
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. (Optional) Create a superuser for Django admin:
```bash
python manage.py createsuperuser
```

6. Start the development server:
```bash
python manage.py runserver
```

7. Access the API documentation:
- Swagger UI: [http://localhost:8000/](http://localhost:8000/)
- Redoc: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

8. (Optional) Access the Django admin:
- [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

**Notes:**
- The default database is SQLite; no additional setup is required.
- All API endpoints are public (no authentication by default).
- Product IDs are assumed to be valid and managed externally.
- For Windows users, use `venv\Scripts\activate` to activate the virtual environment.

## API Endpoints

- `POST /coupons`: Create a new coupon
- `GET /coupons`: Retrieve all coupons
- `GET /coupons/{id}`: Retrieve a specific coupon by ID
- `PUT /coupons/{id}`: Update a specific coupon by ID
- `DELETE /coupons/{id}`: Delete a specific coupon by ID
- `POST /applicable-coupons`: Fetch all applicable coupons for a given cart
- `POST /apply-coupon/{id}`: Apply a specific coupon to the cart

## Coupon Cases

### Implemented Cases

#### 1. Cart-wise Coupons
- **Percentage Discount**: Applies a percentage discount to the entire cart if it exceeds a certain threshold
  - Example: 10% off on carts over $100
- **Fixed Amount Discount**: Applies a fixed amount discount to the entire cart if it exceeds a certain threshold
  - Example: $15 off on carts over $150
- **Free Shipping**: Removes shipping cost if cart exceeds a certain threshold
  - Example: Free shipping on carts over $50

#### 2. Product-wise Coupons
- **Percentage Discount on Specific Product**: Applies a percentage discount to a specific product
  - Example: 20% off on Product A
- **Fixed Amount Discount on Specific Product**: Applies a fixed amount discount to a specific product
  - Example: $5 off on Product B
- **Category Discount**: Applies a discount to all products in a specific category
  - Example: 15% off on all electronics
- **Brand Discount**: Applies a discount to all products of a specific brand
  - Example: 10% off on all Nike products

#### 3. BxGy Coupons (Buy X Get Y)
- **Same Product**: Buy a certain quantity of a product and get additional units of the same product free
  - Example: Buy 2 of Product A, get 1 of Product A free
- **Different Product**: Buy a certain quantity of one product and get another product free
  - Example: Buy 2 of Product A, get 1 of Product B free
- **Product Set**: Buy from a set of products and get free items from another set
  - Example: Buy 2 products from [X, Y, Z], get 1 product free from [A, B, C]
- **Repetition Limit**: Limit how many times a BxGy coupon can be applied
  - Example: Buy 2 get 1 free with a repetition limit of 3 (max 3 free items)

#### 4. Time-Limited Coupons
- **Expiration Date**: Coupons valid only until a specific date
- **Time-of-Day Restriction**: Coupons valid only during specific hours
  - Example: Happy hour discount valid from 2-5 PM

### Non-implemented Cases

#### 1. Advanced Cart-wise Coupons
- **Tiered Discounts**: Different discount percentages based on cart value tiers
  - Example: 5% off on carts over $50, 10% off on carts over $100, 15% off on carts over $200
- **First-time User Discounts**: Special discounts for first-time purchasers
- **Loyalty Tier Discounts**: Different discounts based on customer loyalty level

#### 2. Advanced Product-wise Coupons
- **Bundle Discounts**: Discount when specific product combinations are purchased together
- **Quantity-Based Sliding Scale**: Different discount percentages based on quantity purchased
  - Example: 5% off for 2 items, 10% off for 5 items, 15% off for 10+ items
- **Nth Purchase Discount**: Every nth purchase of a product gets a discount
  - Example: Every 5th coffee is free

#### 3. Complex BxGy Scenarios
- **Buy X from Category A, Get Y from Category B**: Category-based BxGy offers
- **Tiered BxGy**: Different free products based on quantity purchased
  - Example: Buy 2 get 1 free, buy 5 get 3 free, buy 10 get 7 free
- **Cross-sell BxGy**: Buy main product, get accessory free

#### 4. Combination and Exclusion Rules
- **Coupon Stacking**: Rules for combining multiple coupons
- **Exclusions**: Products or categories excluded from coupons
- **Maximum Discount Cap**: Limit on total discount amount

## Limitations and Assumptions

### Limitations
- Coupon stacking is not supported (only one coupon can be applied at a time)
- No user authentication/authorization
- No product database integration (products are referenced by ID only)
- In-memory cart handling (no persistent carts)
- Limited error handling for edge cases

### Assumptions
- Product IDs are valid and exist in an external system
- Cart items include accurate product information
- Percentage discounts are applied to the original price
- BxGy discounts are applied to the lowest-priced eligible products
- For category/brand discounts, category/brand information is included in the request

## Future Improvements
1. Support for coupon stacking with priority rules
2. User authentication and authorization
3. Integration with product database
4. Persistent carts
5. Advanced analytics for coupon usage
6. More complex coupon types
7. Improved error handling
