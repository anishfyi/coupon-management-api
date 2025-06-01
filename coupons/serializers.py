from rest_framework import serializers
from .models import (
    Coupon, 
    CartWiseCoupon, 
    ProductWiseCoupon, 
    BxGyCoupon, 
    BxGyCouponBuyProduct, 
    BxGyCouponGetProduct
)


class CartWiseCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartWiseCoupon
        fields = ['discount_type', 'threshold', 'discount_value']


class ProductWiseCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWiseCoupon
        fields = ['discount_type', 'product_id', 'category', 'brand', 'discount_value']


class BxGyCouponBuyProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = BxGyCouponBuyProduct
        fields = ['product_id', 'quantity']


class BxGyCouponGetProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = BxGyCouponGetProduct
        fields = ['product_id', 'quantity']


class BxGyCouponSerializer(serializers.ModelSerializer):
    buy_products = BxGyCouponBuyProductSerializer(many=True)
    get_products = BxGyCouponGetProductSerializer(many=True)
    
    class Meta:
        model = BxGyCoupon
        fields = ['repetition_limit', 'buy_products', 'get_products']


class CouponSerializer(serializers.ModelSerializer):
    cart_wise_details = CartWiseCouponSerializer(required=False, allow_null=True)
    product_wise_details = ProductWiseCouponSerializer(required=False, allow_null=True)
    bxgy_details = BxGyCouponSerializer(required=False, allow_null=True)
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'type', 'code', 'name', 'description', 
            'is_active', 'created_at', 'updated_at', 'expires_at',
            'cart_wise_details', 'product_wise_details', 'bxgy_details'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """
        Custom validation to ensure only the relevant coupon type details are provided
        """
        coupon_type = data.get('type', getattr(self.instance, 'type', None))
        
        # If type is not provided and we don't have an instance, raise error
        if not coupon_type and not self.instance:
            raise serializers.ValidationError("Coupon type is required")
        
        # If we have an instance, use its type if not provided in update
        if not coupon_type and self.instance:
            coupon_type = self.instance.type
        
        # Validate that only the relevant coupon type details are provided
        if coupon_type == 'cart-wise':
            if 'product_wise_details' in data and data['product_wise_details'] is not None:
                raise serializers.ValidationError("product_wise_details should not be provided for cart-wise coupons")
            if 'bxgy_details' in data and data['bxgy_details'] is not None:
                raise serializers.ValidationError("bxgy_details should not be provided for cart-wise coupons")
        elif coupon_type == 'product-wise':
            if 'cart_wise_details' in data and data['cart_wise_details'] is not None:
                raise serializers.ValidationError("cart_wise_details should not be provided for product-wise coupons")
            if 'bxgy_details' in data and data['bxgy_details'] is not None:
                raise serializers.ValidationError("bxgy_details should not be provided for product-wise coupons")
        elif coupon_type == 'bxgy':
            if 'cart_wise_details' in data and data['cart_wise_details'] is not None:
                raise serializers.ValidationError("cart_wise_details should not be provided for bxgy coupons")
            if 'product_wise_details' in data and data['product_wise_details'] is not None:
                raise serializers.ValidationError("product_wise_details should not be provided for bxgy coupons")
        
        return data
    
    def create(self, validated_data):
        coupon_type = validated_data.get('type')
        
        # Extract nested data based on coupon type
        cart_wise_data = validated_data.pop('cart_wise_details', None)
        product_wise_data = validated_data.pop('product_wise_details', None)
        bxgy_data = validated_data.pop('bxgy_details', None)
        
        # Create the base coupon
        coupon = Coupon.objects.create(**validated_data)
        
        # Create the specific coupon type details
        if coupon_type == 'cart-wise' and cart_wise_data:
            CartWiseCoupon.objects.create(coupon=coupon, **cart_wise_data)
        elif coupon_type == 'product-wise' and product_wise_data:
            ProductWiseCoupon.objects.create(coupon=coupon, **product_wise_data)
        elif coupon_type == 'bxgy' and bxgy_data:
            buy_products_data = bxgy_data.pop('buy_products', [])
            get_products_data = bxgy_data.pop('get_products', [])
            
            # Create BxGy coupon
            bxgy_coupon = BxGyCoupon.objects.create(coupon=coupon, **bxgy_data)
            
            # Create buy products
            for buy_product_data in buy_products_data:
                BxGyCouponBuyProduct.objects.create(bxgy_coupon=bxgy_coupon, **buy_product_data)
                
            # Create get products
            for get_product_data in get_products_data:
                BxGyCouponGetProduct.objects.create(bxgy_coupon=bxgy_coupon, **get_product_data)
        
        return coupon
    
    def update(self, instance, validated_data):
        # Get the coupon type - use existing type if not provided in update
        coupon_type = validated_data.get('type', instance.type)
        
        # Only process the details for the current coupon type
        if coupon_type == 'cart-wise':
            cart_wise_data = validated_data.pop('cart_wise_details', None)
            validated_data.pop('product_wise_details', None)  # Ignore other types
            validated_data.pop('bxgy_details', None)  # Ignore other types
            
            # Update the base coupon
            instance = super().update(instance, validated_data)
            
            # Update cart-wise details if provided
            if cart_wise_data:
                cart_wise_coupon, created = CartWiseCoupon.objects.get_or_create(coupon=instance)
                for key, value in cart_wise_data.items():
                    setattr(cart_wise_coupon, key, value)
                cart_wise_coupon.save()
            
        elif coupon_type == 'product-wise':
            product_wise_data = validated_data.pop('product_wise_details', None)
            validated_data.pop('cart_wise_details', None)  # Ignore other types
            validated_data.pop('bxgy_details', None)  # Ignore other types
            
            # Update the base coupon
            instance = super().update(instance, validated_data)
            
            # Update product-wise details if provided
            if product_wise_data:
                product_wise_coupon, created = ProductWiseCoupon.objects.get_or_create(coupon=instance)
                for key, value in product_wise_data.items():
                    setattr(product_wise_coupon, key, value)
                product_wise_coupon.save()
            
        elif coupon_type == 'bxgy':
            bxgy_data = validated_data.pop('bxgy_details', None)
            validated_data.pop('cart_wise_details', None)  # Ignore other types
            validated_data.pop('product_wise_details', None)  # Ignore other types
            
            # Update the base coupon
            instance = super().update(instance, validated_data)
            
            # Update bxgy details if provided
            if bxgy_data:
                buy_products_data = bxgy_data.pop('buy_products', [])
                get_products_data = bxgy_data.pop('get_products', [])
                
                # Update BxGy coupon
                bxgy_coupon, created = BxGyCoupon.objects.get_or_create(coupon=instance)
                for key, value in bxgy_data.items():
                    setattr(bxgy_coupon, key, value)
                bxgy_coupon.save()
                
                # Handle buy products
                if buy_products_data:
                    # Delete existing buy products
                    bxgy_coupon.buy_products.all().delete()
                    
                    # Create new buy products
                    for buy_product_data in buy_products_data:
                        BxGyCouponBuyProduct.objects.create(bxgy_coupon=bxgy_coupon, **buy_product_data)
                
                # Handle get products
                if get_products_data:
                    # Delete existing get products
                    bxgy_coupon.get_products.all().delete()
                    
                    # Create new get products
                    for get_product_data in get_products_data:
                        BxGyCouponGetProduct.objects.create(bxgy_coupon=bxgy_coupon, **get_product_data)
        else:
            # If no specific type details to update, just update the base coupon
            instance = super().update(instance, validated_data)
        
        return instance


# Cart Item and Cart Serializers for API requests
class CartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    
    # Optional fields for category and brand
    category = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    brand = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True)


# Response Serializers

class DiscountedCartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    total_discount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)


class DiscountedCartSerializer(serializers.Serializer):
    items = DiscountedCartItemSerializer(many=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    total_discount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)


class ApplicableCouponSerializer(serializers.Serializer):
    coupon_id = serializers.UUIDField()
    type = serializers.CharField()
    name = serializers.CharField()
    code = serializers.CharField()
    discount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    

class ApplicableCouponsResponseSerializer(serializers.Serializer):
    applicable_coupons = ApplicableCouponSerializer(many=True) 