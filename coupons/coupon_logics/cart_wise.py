from decimal import Decimal


def is_applicable(coupon, cart):
    """
    Check if a cart-wise coupon is applicable to the given cart.
    
    Args:
        coupon: A Coupon object with cart_wise_details
        cart: A dictionary containing cart items
        
    Returns:
        bool: True if the coupon is applicable, False otherwise
    """
    if not hasattr(coupon, 'cart_wise_details'):
        return False
    
    cart_wise_details = coupon.cart_wise_details
    cart_total = calculate_cart_total(cart)
    
    # Check if cart total exceeds the threshold
    return cart_total >= cart_wise_details.threshold


def calculate_discount(coupon, cart):
    """
    Calculate the discount amount for a cart-wise coupon.
    
    Args:
        coupon: A Coupon object with cart_wise_details
        cart: A dictionary containing cart items
        
    Returns:
        Decimal: The discount amount
    """
    if not is_applicable(coupon, cart):
        return Decimal('0.00')
    
    cart_wise_details = coupon.cart_wise_details
    cart_total = calculate_cart_total(cart)
    
    if cart_wise_details.discount_type == 'percentage':
        # Calculate percentage discount
        return (cart_total * cart_wise_details.discount_value / 100).quantize(Decimal('0.01'))
    elif cart_wise_details.discount_type == 'fixed':
        # Apply fixed amount discount
        return min(cart_wise_details.discount_value, cart_total).quantize(Decimal('0.01'))
    elif cart_wise_details.discount_type == 'shipping':
        # For simplicity, assuming shipping is free (discount equals shipping cost)
        # In a real system, shipping cost would be calculated based on order details
        shipping_cost = Decimal('5.00')  # Placeholder value
        return shipping_cost.quantize(Decimal('0.01'))
    
    return Decimal('0.00')


def apply_discount(coupon, cart):
    """
    Apply the cart-wise coupon discount to the cart.
    
    Args:
        coupon: A Coupon object with cart_wise_details
        cart: A dictionary containing cart items
        
    Returns:
        dict: The updated cart with discounts applied
    """
    if not is_applicable(coupon, cart):
        return create_discounted_cart(cart, Decimal('0.00'))
    
    # Calculate the total discount
    total_discount = calculate_discount(coupon, cart)
    
    # Create a discounted cart
    return create_discounted_cart(cart, total_discount)


def calculate_cart_total(cart):
    """
    Calculate the total value of the cart.
    
    Args:
        cart: A dictionary containing cart items
        
    Returns:
        Decimal: The total cart value
    """
    total = Decimal('0.00')
    
    for item in cart.get('items', []):
        item_total = Decimal(str(item['price'])) * item['quantity']
        total += item_total
    
    return total.quantize(Decimal('0.01'))


def create_discounted_cart(cart, total_discount):
    """
    Create a new cart object with the discount applied.
    
    Args:
        cart: A dictionary containing cart items
        total_discount: The total discount to apply
        
    Returns:
        dict: The updated cart with discount applied
    """
    # Calculate cart total
    total_price = calculate_cart_total(cart)
    
    # Calculate final price
    final_price = max(Decimal('0.00'), total_price - total_discount)
    
    # Create discounted cart items (cart-wise discount affects only the total, not individual items)
    discounted_items = []
    for item in cart.get('items', []):
        discounted_items.append({
            'product_id': item['product_id'],
            'quantity': item['quantity'],
            'price': item['price'],
            'total_discount': Decimal('0.00')  # Individual items don't have discounts in cart-wise coupon
        })
    
    # Create the discounted cart
    discounted_cart = {
        'items': discounted_items,
        'total_price': total_price,
        'total_discount': total_discount,
        'final_price': final_price
    }
    
    return discounted_cart 