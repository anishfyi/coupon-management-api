from decimal import Decimal
from collections import defaultdict


def is_applicable(coupon, cart):
    """
    Check if a BxGy coupon is applicable to the given cart.
    
    Args:
        coupon: A Coupon object with bxgy_details
        cart: A dictionary containing cart items
        
    Returns:
        bool: True if the coupon is applicable, False otherwise
    """
    if not hasattr(coupon, 'bxgy_details'):
        return False
    
    bxgy_details = coupon.bxgy_details
    buy_products = {bp.product_id: bp.quantity for bp in bxgy_details.buy_products.all()}
    get_products = {gp.product_id: gp.quantity for gp in bxgy_details.get_products.all()}
    
    if not buy_products or not get_products:
        return False
    
    # Check if cart contains required buy products
    cart_products = defaultdict(int)
    for item in cart.get('items', []):
        cart_products[item['product_id']] += item['quantity']
    
    # Check if cart has at least one set of required buy products
    for product_id, required_quantity in buy_products.items():
        if cart_products[product_id] < required_quantity:
            return False
    
    # Also check if cart has at least one of the get products
    for product_id in get_products.keys():
        if product_id in cart_products:
            return True
    
    return False


def calculate_discount(coupon, cart):
    """
    Calculate the discount amount for a BxGy coupon.
    
    Args:
        coupon: A Coupon object with bxgy_details
        cart: A dictionary containing cart items
        
    Returns:
        Decimal: The discount amount
    """
    if not is_applicable(coupon, cart):
        return Decimal('0.00')
    
    # Get the number of times the BxGy coupon can be applied
    repetition_count = calculate_repetition_count(coupon, cart)
    if repetition_count == 0:
        return Decimal('0.00')
    
    # Calculate the discount (the value of the free products)
    total_discount = Decimal('0.00')
    
    # Find the eligible "get" products in the cart and calculate their values
    bxgy_details = coupon.bxgy_details
    get_products = {gp.product_id: gp.quantity for gp in bxgy_details.get_products.all()}
    
    # Create a list of cart items that match the "get" products for easy sorting
    eligible_get_items = []
    for item in cart.get('items', []):
        if item['product_id'] in get_products:
            eligible_get_items.append({
                'product_id': item['product_id'],
                'price': Decimal(str(item['price'])),
                'quantity': item['quantity'],
                'required_quantity': get_products[item['product_id']]
            })
    
    # Sort eligible get items by price (lowest first to maximize discount value)
    eligible_get_items.sort(key=lambda x: x['price'])
    
    # Apply the discount to as many repetitions as possible
    remaining_repetitions = repetition_count
    
    for item in eligible_get_items:
        if remaining_repetitions <= 0:
            break
            
        # Calculate how many free items we can give from this product
        max_free_items = item['quantity']
        required_quantity = item['required_quantity']
        
        # Determine how many repetitions we can apply to this product
        repeats_for_this_product = min(
            remaining_repetitions,
            max_free_items // required_quantity
        )
        
        if repeats_for_this_product > 0:
            # Calculate how many items are free
            free_items = repeats_for_this_product * required_quantity
            
            # Calculate discount for these free items
            item_discount = free_items * item['price']
            total_discount += item_discount
            
            # Update remaining repetitions
            remaining_repetitions -= repeats_for_this_product
    
    return total_discount.quantize(Decimal('0.01'))


def apply_discount(coupon, cart):
    """
    Apply the BxGy coupon discount to the cart.
    
    Args:
        coupon: A Coupon object with bxgy_details
        cart: A dictionary containing cart items
        
    Returns:
        dict: The updated cart with discounts applied
    """
    if not is_applicable(coupon, cart):
        return create_discounted_cart(cart, {})
    
    # Get the number of times the BxGy coupon can be applied
    repetition_count = calculate_repetition_count(coupon, cart)
    if repetition_count == 0:
        return create_discounted_cart(cart, {})
    
    # Find the eligible "get" products and apply discounts
    bxgy_details = coupon.bxgy_details
    get_products = {gp.product_id: gp.quantity for gp in bxgy_details.get_products.all()}
    
    # Create a list of cart items that match the "get" products for easy sorting
    eligible_get_items = []
    for idx, item in enumerate(cart.get('items', [])):
        if item['product_id'] in get_products:
            eligible_get_items.append({
                'index': idx,
                'product_id': item['product_id'],
                'price': Decimal(str(item['price'])),
                'quantity': item['quantity'],
                'required_quantity': get_products[item['product_id']]
            })
    
    # Sort eligible get items by price (lowest first to maximize discount value)
    eligible_get_items.sort(key=lambda x: x['price'])
    
    # Apply the discount to as many repetitions as possible
    remaining_repetitions = repetition_count
    item_discounts = {}
    
    for item in eligible_get_items:
        if remaining_repetitions <= 0:
            break
            
        # Calculate how many free items we can give from this product
        max_free_items = item['quantity']
        required_quantity = item['required_quantity']
        
        # Determine how many repetitions we can apply to this product
        repeats_for_this_product = min(
            remaining_repetitions,
            max_free_items // required_quantity
        )
        
        if repeats_for_this_product > 0:
            # Calculate how many items are free
            free_items = repeats_for_this_product * required_quantity
            
            # Calculate discount for these free items
            item_discount = free_items * item['price']
            item_discounts[item['index']] = item_discount.quantize(Decimal('0.01'))
            
            # Update remaining repetitions
            remaining_repetitions -= repeats_for_this_product
    
    # Create discounted cart
    return create_discounted_cart(cart, item_discounts)


def calculate_repetition_count(coupon, cart):
    """
    Calculate how many times the BxGy coupon can be applied based on cart contents.
    
    Args:
        coupon: A Coupon object with bxgy_details
        cart: A dictionary containing cart items
        
    Returns:
        int: The number of times the coupon can be applied
    """
    bxgy_details = coupon.bxgy_details
    buy_products = {bp.product_id: bp.quantity for bp in bxgy_details.buy_products.all()}
    
    # Count the available buy products in the cart
    cart_products = defaultdict(int)
    for item in cart.get('items', []):
        cart_products[item['product_id']] += item['quantity']
    
    # Calculate how many complete sets of buy products are in the cart
    set_counts = []
    for product_id, required_quantity in buy_products.items():
        if required_quantity <= 0:  # Avoid division by zero
            continue
        set_counts.append(cart_products[product_id] // required_quantity)
    
    if not set_counts:
        return 0
    
    # The number of complete sets is the minimum count across all required products
    complete_sets = min(set_counts)
    
    # Limit by the repetition limit
    repetition_limit = bxgy_details.repetition_limit
    
    return min(complete_sets, repetition_limit)


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
        
        # For BxGy coupons, handle the case where we need to add free items
        # In this simplified implementation, we're just applying a discount to existing items
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