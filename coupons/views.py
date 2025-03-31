from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Coupon
from .serializers import (
    CouponSerializer, 
    CartSerializer, 
    DiscountedCartSerializer,
    ApplicableCouponsResponseSerializer,
    ApplicableCouponSerializer
)
from .services import get_applicable_coupons, apply_coupon


class CouponViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on coupons.
    """
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer


class ApplicableCouponsView(APIView):
    """
    View to get all applicable coupons for a cart.
    """
    @swagger_auto_schema(
        request_body=CartSerializer,
        responses={
            200: ApplicableCouponsResponseSerializer,
            400: 'Bad Request',
        }
    )
    def post(self, request, format=None):
        """
        Get all applicable coupons for the given cart.
        """
        serializer = CartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        cart = serializer.validated_data
        applicable_coupons = get_applicable_coupons(cart)
        
        response_data = {
            'applicable_coupons': applicable_coupons
        }
        
        response_serializer = ApplicableCouponsResponseSerializer(data=response_data)
        response_serializer.is_valid()  # We can assume it's valid since we constructed it
        
        return Response(response_serializer.data)


class ApplyCouponView(APIView):
    """
    View to apply a specific coupon to a cart.
    """
    @swagger_auto_schema(
        request_body=CartSerializer,
        responses={
            200: DiscountedCartSerializer,
            400: 'Bad Request',
            404: 'Coupon not found or not applicable',
        }
    )
    def post(self, request, id, format=None):
        """
        Apply a specific coupon to the cart.
        """
        serializer = CartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        cart = serializer.validated_data
        discounted_cart = apply_coupon(id, cart)
        
        if discounted_cart is None:
            return Response(
                {'error': 'Coupon not found or not applicable to the cart'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        response_serializer = DiscountedCartSerializer(data=discounted_cart)
        response_serializer.is_valid()  # We can assume it's valid since we constructed it
        
        return Response(response_serializer.data)
