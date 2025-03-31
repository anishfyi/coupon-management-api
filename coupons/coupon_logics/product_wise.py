from decimal import Decimal


def is_applicable(coupon, cart):
    """
    Check if a product-wise coupon is applicable to the given cart.
    
    Args:
        coupon: A Coupon object with product_wise_details
        cart: A dictionary containing cart items
        
    Returns:
        bool: True if the coupon is applicable, False otherwise
    """
    if not hasattr(coupon, 'product_wise_details'):
        return False
    
    product_wise_details = coupon.product_wise_details
    
    # Check if cart contains product that matches coupon criteria
    for item in cart.get('items', []):
        if matches_product_criteria(item, product_wise_details):
            return True
    
    return False


def calculate_discount(coupon, cart):
    """
    Calculate the discount amount for a product-wise coupon.
    
    Args:
        coupon: A Coupon object with product_wise_details
        cart: A dictionary containing cart items
        
    Returns:
        Decimal: The discount amount
    """
    if not is_applicable(coupon, cart):
        return Decimal('0.00')
    
    product_wise_details = coupon.product_wise_details
    total_discount = Decimal('0.00')
    
    for item in cart.get('items', []):
        if matches_product_criteria(item, product_wise_details):
            item_price = Decimal(str(item['price']))
            quantity = item['quantity']
            
            if product_wise_details.discount_type == 'percentage':
                # Calculate percentage discount
                item_discount = (item_price * product_wise_details.discount_value / 100) * quantity
            else:  # fixed discount
                # Apply fixed amount discount per item, but not more than the item price
                item_discount = min(product_wise_details.discount_value, item_price) * quantity
            
            total_discount += item_discount
    
    return total_discount.quantize(Decimal('0.01'))


def apply_discount(coupon, cart):
    """
    Apply the product-wise coupon discount to the cart.
    
    Args:
        coupon: A Coupon object with product_wise_details
        cart: A dictionary containing cart items
        
    Returns:
        dict: The updated cart with discounts applied
    """
    if not is_applicable(coupon, cart):
        return create_discounted_cart(cart, {})
    
    product_wise_details = coupon.product_wise_details
    discounted_items = []
    item_discounts = {}
    
    # Calculate discounts for each item
    for idx, item in enumerate(cart.get('items', [])):
        if matches_product_criteria(item, product_wise_details):
            item_price = Decimal(str(item['price']))
            quantity = item['quantity']
            
            if product_wise_details.discount_type == 'percentage':
                # Calculate percentage discount
                per_item_discount = item_price * product_wise_details.discount_value / 100
            else:  # fixed discount
                # Apply fixed amount discount per item, but not more than the item price
                per_item_discount = min(product_wise_details.discount_value, item_price)
            
            item_discount = per_item_discount * quantity
            item_discounts[idx] = item_discount.quantize(Decimal('0.01'))
    
    # Create discounted cart
    return create_discounted_cart(cart, item_discounts)


def matches_product_criteria(item, product_wise_details):
    """
    Check if a cart item matches the product-wise coupon criteria.
    
    Args:
        item: A cart item
        product_wise_details: Product-wise coupon details
        
    Returns:
        bool: True if the item matches the criteria, False otherwise
    """
    # Check if matches by product_id
    if product_wise_details.product_id and item['product_id'] == product_wise_details.product_id:
        return True
    
    # Check if matches by category
    if product_wise_details.category and 'category' in item and item['category'] == product_wise_details.category:
        return True
    
    # Check if matches by brand
    if product_wise_details.brand and 'brand' in item and item['brand'] == product_wise_details.brand:
        return True
    
    return False


def create_discounted_cart(cart, item_discounts):
    """
    Create a new cart object with the discount applied to specific items.
    
    Args:
        cart: A dictionary containing cart items
        item_discounts: Dictionary mapping item index to discount amount
        
    Returns:
        dict: The updated cart with discount applied
    """
    discounted_items = []
    total_price = Decimal('0.00')
    total_discount = Decimal('0.00')
    
    # Create discounted cart items
    for idx, item in enumerate(cart.get('items', [])):
        item_price = Decimal(str(item['price']))
        quantity = item['quantity']
        item_total = item_price * quantity
        total_price += item_total
        
        item_discount = item_discounts.get(idx, Decimal('0.00'))
        total_discount += item_discount
        
        discounted_items.append({
            'product_id': item['product_id'],
            'quantity': item['quantity'],
            'price': item_price,
            'total_discount': item_discount
        })
    
    # Calculate final price
    final_price = max(Decimal('0.00'), total_price - total_discount)
    
    # Create the discounted cart
    discounted_cart = {
        'items': discounted_items,
        'total_price': total_price.quantize(Decimal('0.01')),
        'total_discount': total_discount.quantize(Decimal('0.01')),
        'final_price': final_price.quantize(Decimal('0.01'))
    }
    
    return discounted_cart 