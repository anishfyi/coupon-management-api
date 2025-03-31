from django.db import models
from django.utils import timezone
from decimal import Decimal
import uuid

class Coupon(models.Model):
    """Base coupon model that holds common information for all coupon types"""
    COUPON_TYPE_CHOICES = (
        ('cart-wise', 'Cart-wise Coupon'),
        ('product-wise', 'Product-wise Coupon'),
        ('bxgy', 'Buy X Get Y Coupon'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=20, choices=COUPON_TYPE_CHOICES)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def is_expired(self):
        """Check if the coupon is expired"""
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if the coupon is valid (active and not expired)"""
        return self.is_active and not self.is_expired()


class CartWiseCoupon(models.Model):
    """Cart-wise coupon details"""
    coupon = models.OneToOneField(
        Coupon, 
        on_delete=models.CASCADE, 
        related_name='cart_wise_details'
    )
    discount_type = models.CharField(
        max_length=10,
        choices=(
            ('percentage', 'Percentage'),
            ('fixed', 'Fixed Amount'),
            ('shipping', 'Free Shipping'),
        ),
        default='percentage'
    )
    threshold = models.DecimalField(max_digits=10, decimal_places=2)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        if self.discount_type == 'percentage':
            return f"{self.discount_value}% off on carts over ${self.threshold}"
        elif self.discount_type == 'fixed':
            return f"${self.discount_value} off on carts over ${self.threshold}"
        else:
            return f"Free shipping on carts over ${self.threshold}"


class ProductWiseCoupon(models.Model):
    """Product-wise coupon details"""
    coupon = models.OneToOneField(
        Coupon, 
        on_delete=models.CASCADE, 
        related_name='product_wise_details'
    )
    discount_type = models.CharField(
        max_length=10,
        choices=(
            ('percentage', 'Percentage'),
            ('fixed', 'Fixed Amount'),
        ),
        default='percentage'
    )
    product_id = models.IntegerField(null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    brand = models.CharField(max_length=100, null=True, blank=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        if self.product_id:
            target = f"Product #{self.product_id}"
        elif self.category:
            target = f"Category: {self.category}"
        elif self.brand:
            target = f"Brand: {self.brand}"
        else:
            target = "Unknown product"
            
        if self.discount_type == 'percentage':
            return f"{self.discount_value}% off on {target}"
        else:
            return f"${self.discount_value} off on {target}"


class BxGyCoupon(models.Model):
    """Buy X Get Y coupon details"""
    coupon = models.OneToOneField(
        Coupon, 
        on_delete=models.CASCADE, 
        related_name='bxgy_details'
    )
    repetition_limit = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        buy_products = self.buy_products.all()
        get_products = self.get_products.all()
        
        if not buy_products or not get_products:
            return f"BxGy Coupon (incomplete configuration)"
        
        buy_str = ", ".join([f"{bp.quantity} of Product #{bp.product_id}" for bp in buy_products])
        get_str = ", ".join([f"{gp.quantity} of Product #{gp.product_id}" for gp in get_products])
        
        return f"Buy {buy_str}, Get {get_str} (limit: {self.repetition_limit})"


class BxGyCouponBuyProduct(models.Model):
    """Products that need to be bought for BxGy coupon"""
    bxgy_coupon = models.ForeignKey(
        BxGyCoupon, 
        on_delete=models.CASCADE, 
        related_name='buy_products'
    )
    product_id = models.IntegerField()
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"Buy {self.quantity} of Product #{self.product_id}"


class BxGyCouponGetProduct(models.Model):
    """Products that are given free for BxGy coupon"""
    bxgy_coupon = models.ForeignKey(
        BxGyCoupon, 
        on_delete=models.CASCADE, 
        related_name='get_products'
    )
    product_id = models.IntegerField()
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"Get {self.quantity} of Product #{self.product_id} free"
