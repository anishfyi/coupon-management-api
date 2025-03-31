from decimal import Decimal
from django.utils import timezone
from .models import Coupon
from .coupon_logics import cart_wise, product_wise, bxgy


def get_applicable_coupons(cart):
    """
    Get all applicable coupons for the given cart.
    
    Args:
        cart: A dictionary containing cart items
        
    Returns:
        list: A list of applicable coupons with their discount amounts
    """
    all_coupons = Coupon.objects.filter(is_active=True)
    applicable_coupons = []
    
    for coupon in all_coupons:
        # Skip expired coupons
        if coupon.is_expired():
            continue
        
        # Check if coupon is applicable based on type
        is_applicable = False
        discount_amount = Decimal('0.00')
        
        if coupon.type == 'cart-wise':
            is_applicable = cart_wise.is_applicable(coupon, cart)
            if is_applicable:
                discount_amount = cart_wise.calculate_discount(coupon, cart)
        
        elif coupon.type == 'product-wise':
            is_applicable = product_wise.is_applicable(coupon, cart)
            if is_applicable:
                discount_amount = product_wise.calculate_discount(coupon, cart)
        
        elif coupon.type == 'bxgy':
            is_applicable = bxgy.is_applicable(coupon, cart)
            if is_applicable:
                discount_amount = bxgy.calculate_discount(coupon, cart)
        
        # If applicable and provides a discount, add to list
        if is_applicable and discount_amount > Decimal('0.00'):
            applicable_coupons.append({
                'coupon_id': coupon.id,
                'type': coupon.type,
                'name': coupon.name,
                'code': coupon.code,
                'discount': discount_amount
            })
    
    # Sort by discount amount (highest first)
    applicable_coupons.sort(key=lambda x: x['discount'], reverse=True)
    
    return applicable_coupons


def apply_coupon(coupon_id, cart):
    """
    Apply a specific coupon to the cart.
    
    Args:
        coupon_id: The ID of the coupon to apply
        cart: A dictionary containing cart items
        
    Returns:
        dict: The updated cart with discounts applied, or None if coupon is not applicable
    """
    try:
        coupon = Coupon.objects.get(id=coupon_id, is_active=True)
    except Coupon.DoesNotExist:
        return None
    
    # Skip expired coupons
    if coupon.is_expired():
        return None
    
    # Apply coupon based on type
    if coupon.type == 'cart-wise':
        if cart_wise.is_applicable(coupon, cart):
            return cart_wise.apply_discount(coupon, cart)
    
    elif coupon.type == 'product-wise':
        if product_wise.is_applicable(coupon, cart):
            return product_wise.apply_discount(coupon, cart)
    
    elif coupon.type == 'bxgy':
        if bxgy.is_applicable(coupon, cart):
            return bxgy.apply_discount(coupon, cart)
    
    # Coupon not applicable
    return None 