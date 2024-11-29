from rest_framework.routers import DefaultRouter
from user.views import UserViewSet,RegisterViewSet,ResendOtpViewSet,LoginViewSet,ForgotPasswordViewSet,ResetPasswordViewSet,ChangePasswordViewSet,LoginWithGoogleViewSet,VerifyEmailViewset

from support_ticket.views import SupportTicketPagesViewSet
from menukit.views import CategoryViewSet,SubCategoryViewSet
from orders.views import OrderViewSet,OrderItemViewSet


router=DefaultRouter()


router.register("user",UserViewSet,basename="user")
router.register("register",RegisterViewSet,basename="register")

router.register("verify-otp",VerifyEmailViewset,basename="verify-otp")
router.register("resend-otp",ResendOtpViewSet,basename="resend-otp")
router.register("login",LoginViewSet,basename="login")
router.register("forgot-password",ForgotPasswordViewSet,basename="forgot-password")
router.register("reset-password",ResetPasswordViewSet,basename="reset-password")
router.register("change-password",ChangePasswordViewSet,basename="change-password")
router.register("google-authentication",LoginWithGoogleViewSet,basename="google-authentication")
router.register("support-ticket",SupportTicketPagesViewSet,basename="support-ticket")
router.register("category",CategoryViewSet,basename="category")
router.register("subcategory",SubCategoryViewSet,basename="subcategory")
router.register("orders",OrderViewSet,basename="orders")
router.register("order-item",OrderItemViewSet,basename="order-item")









