from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CouponViewSet, ApplicableCouponsView, ApplyCouponView

router = DefaultRouter()
router.register(r'coupons', CouponViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('applicable-coupons/', ApplicableCouponsView.as_view(), name='applicable-coupons'),
    path('apply-coupon/<uuid:id>/', ApplyCouponView.as_view(), name='apply-coupon'),
] 