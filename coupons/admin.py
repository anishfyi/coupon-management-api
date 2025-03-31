from django.contrib import admin
from .models import (
    Coupon, 
    CartWiseCoupon, 
    ProductWiseCoupon, 
    BxGyCoupon,
    BxGyCouponBuyProduct,
    BxGyCouponGetProduct
)


class CartWiseCouponInline(admin.StackedInline):
    model = CartWiseCoupon
    can_delete = False
    verbose_name_plural = 'Cart-wise Coupon Details'


class ProductWiseCouponInline(admin.StackedInline):
    model = ProductWiseCoupon
    can_delete = False
    verbose_name_plural = 'Product-wise Coupon Details'


class BxGyCouponBuyProductInline(admin.TabularInline):
    model = BxGyCouponBuyProduct
    extra = 1
    verbose_name_plural = 'Buy Products'


class BxGyCouponGetProductInline(admin.TabularInline):
    model = BxGyCouponGetProduct
    extra = 1
    verbose_name_plural = 'Get Products'


class BxGyCouponInline(admin.StackedInline):
    model = BxGyCoupon
    can_delete = False
    verbose_name_plural = 'BxGy Coupon Details'


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'type', 'is_active', 'expires_at')
    list_filter = ('type', 'is_active')
    search_fields = ('name', 'code')
    
    def get_inlines(self, request, obj=None):
        if obj is None:
            return []
        
        if obj.type == 'cart-wise':
            return [CartWiseCouponInline]
        elif obj.type == 'product-wise':
            return [ProductWiseCouponInline]
        elif obj.type == 'bxgy':
            return [BxGyCouponInline, BxGyCouponBuyProductInline, BxGyCouponGetProductInline]
        
        return []


@admin.register(BxGyCoupon)
class BxGyCouponAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'repetition_limit')
    inlines = [BxGyCouponBuyProductInline, BxGyCouponGetProductInline]
