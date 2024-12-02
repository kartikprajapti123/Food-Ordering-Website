from django.shortcuts import render
# Create your views here.
import requests
from rest_framework.filters import SearchFilter,OrderingFilter
from user.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.viewsets import ModelViewSet
from user.serializer import UserSerializer,RegisterSerializer,OtpSerilaizer
from utils.pagination import mypagination
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
import threading
from utils.send_mail import send_email_with_template
from django.db import transaction
from utils.generate_otp import generate_otp,generate_token,decode_token
from rest_framework_simplejwt.tokens import RefreshToken

from faker import Faker
# from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken

from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken


from rest_framework import status
from decouple import config
from django.contrib.auth.hashers import check_password

faker=Faker()
class UserViewSet(ModelViewSet):
    queryset=User.objects.filter(deleted=0,is_active=True)
    serializer_class=UserSerializer
    pagination_class=mypagination
    filter_backends=[SearchFilter,OrderingFilter]
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    
    search_fields=[
        "username",
        
        "email"
    ]
    ordering_fields=[
        
        "username",
        "email"
    ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        no_pagination = request.query_params.get("no_pagination")

        if no_pagination:
            serializer = self.serializer_class(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response({"success": True, "data": serializer.data})

        serializer = self.serializer_class(queryset, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance=self.get_object()
        data=request.data 
        serializer=self.serializer_class(instance=instance,data=data,partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True,"message":"Successfully Updated","data": serializer.data}, status=status.HTTP_200_OK)
        
        return Response({"success": True,"message":serializer.errors}, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['post'])
    def logout(self, request, *args, **kwargs):
        try:
            # Get the token from the request body
            token = request.data.get('refresh_token')
            print("Refresh token received:", token)

            if token:
                try:
                    # Convert to RefreshToken object
                    refresh_token = RefreshToken(token)

                    # Get the user associated with the token
                    user_id = refresh_token.payload.get('user_id')
                    user = User.objects.filter(id=user_id).first()

                    if user:
                        # Deactivate the user (make them inactive)
                        user.is_active = False
                        user.save()

                        return Response(
                            {'success': True, 'message': 'User logged out and deactivated successfully.'},
                            status=status.HTTP_200_OK
                        )
                    else:
                        return Response(
                            {'success': False, 'message': 'User not found or invalid token.'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                except Exception as e:
                    print("Error during logout:", e)
                    return Response(
                        {'success': False, 'message': 'Error processing token. Try again.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {'success': False, 'message': 'Token not provided.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            print("Unexpected error:", e)
            return Response(
                {'success': False, 'message': 'An unexpected error occurred.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
     
    @action(detail=False, methods=["GET"], url_path="get-user-single")
    def get_user_single(self, request, *args, **kwargs):
        # Get the current logged-in user
        try:
            instance = User.objects.get(id=request.user.id)  # Get the user by ID
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is active
        if not instance.is_active:
            return Response({"detail": "User is not active"}, status=status.HTTP_400_BAD_REQUEST)
 
        if instance:
            serializer=UserSerializer(instance)
            return Response({"success":True,"data":serializer.data},status=status.HTTP_200_OK)
        else:
            return Response({"success":False,"message":"No user found ! Please login again"},status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=False,methods=["GET"],url_path="get-user-multiple")
    def get_user_multiple(self,request,*args,**kwargs):
        instance=request.user
        if instance.is_superuser:
            data=User.objects.all()
            serializer=UserSerializer(data=data,many=True)
            return Response({"success":True,"data":serializer.data},status=status.HTTP_200_OK)
        else:
            return Response({"success":False,"message":"You are not admin"},status=status.HTTP_200_OK)
            
        
class RegisterViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                email = serializer.validated_data["email"]
                user = User.objects.filter(email=email).first()

                if user and not user.email_verified:
                    # User exists but email is not verified, update OTP and resend email
                    user.otp = generate_otp()
                    print(user.otp)
                    user.save()
                else:
                    # Create a new user
                    user = serializer.save()
                    print(user.otp)

                token = generate_token(email, 60)
                subject = "Email Verification"
                to = email
                context = {
                    "link": f"{config('HOST_URL')}verify-otp/{token}/",
                    "otp": user.otp,
                }
                # send_email_verfication(subject=subject, to=to, context=context)
                # subject, recipient_email, template_name, context
                email_thread = threading.Thread(
                    target=send_email_with_template, args=(subject, to, "send_otp.html",context)
                )
                email_thread.start()
                return Response(
                    {
                        "success": True,
                        "message": f"Registration successfully done! OTP has been sent on {user.email} for verification.",
                        "data": serializer.data,
                        "token": token,
                    },
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {"success": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )


# @method_decorator(csrf_exempt, name="dispatch")
class VerifyEmailViewset(ModelViewSet):
    queryset = User.objects.all()

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        otp = int(request.data.get("otp"))
        token=request.data.get("token")
        try:
            payload = decode_token(token)
        except Exception:
            return Response(
                {"success": False, "message": "Invalid or Expired Links"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if "email" not in payload:
            return Response(
                {"success": False, "message": "Invalid Link"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = User.objects.filter(email=payload["email"]).first()
        print(user.otp)
        if user is None:
            return Response(
                {"success": False, "message": "Email is not registered"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not (user.otp == otp):
            return Response(
                {"success": False, "message": "Invalid otp"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user.email_verified = True
        refresh_token = RefreshToken.for_user(user)
        access_token = str(refresh_token.access_token)

        user.otp = otp
        user.is_active=True
        user.save()

        return Response(
            {
                "success": True,
                "message": "Email successfully verified",
                "token": {
                    "access_token": access_token,
                    "refresh_token": str(refresh_token),
                },
            },
            status=status.HTTP_200_OK,
        )

                

# class ResendOtpViewSet(ModelViewSet):

#     @transaction.atomic()
#     def create(self, request, *args, **kwargs):
#         data=request.data
#         user = User.objects.filter(email=data.get('email')).first()
#         if user is None:
#             return Response(
#                 {"success": False, "message": "Email is not registered"},
#                 status=status.HTTP_401_UNAUTHORIZED,
#             )
#         otp=generate_otp()
#         user.otp=otp
#         user.save()
#         subject="Otp for verification email"
#         recipient_email=user.email
#         template_name="send_otp.html"
#         context={
#             "otp":otp
#         }
#         mail_thread = threading.Thread(
#             target=send_email_with_template, 
#             args=(subject, recipient_email, template_name, context)
#         )
#         mail_thread.start()

#         return Response(
#             {"success": True, "message": "An OTP has been sent again to your address."},
#             status=status.HTTP_200_OK,
#         )


class ResendOtpViewSet(ModelViewSet):

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        token=request.data.get("token")
        try:
            payload = decode_token(token)
        except Exception:
            return Response(
                {"success": False, "message": "Link Expired"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if "email" not in payload:
            return Response(
                {"success": False, "message": "Invalid Link"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = User.objects.filter(email=payload["email"]).first()
        if user is None:
            return Response(
                {"success": False, "message": "Email is not registered"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        otp = generate_otp()
        print(otp)
        
        user.otp=otp
        user.save()
        subject = "Email Verification"
        to = user.email
        context = {
            "link": f"{config('HOST_URL')}verify-otp/{token}/",
            "otp": user.otp,
        }
        print(context)
        email_thread = threading.Thread(
            target=send_email_with_template, args=(subject, to, "send_otp.html",context)
        )
        email_thread.start()

        return Response(
            {"success": True, "message": f"An OTP has been sent again to {user.email} ."},
            status=status.HTTP_200_OK,
        )

            

class LoginViewSet(ModelViewSet):

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        data = request.data
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": "Invalid Email or Password"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if check_password(password, user.password) and user.email_verified:
                user.is_active=True
                user.save()
                refresh_token = RefreshToken.for_user(user)
                access_token = str(refresh_token.access_token)

                return Response(
                    {
                        "success": True,
                        "message": "Login successful done",
                        "token": {
                            "access_token": access_token,
                            "refresh_token": str(refresh_token),
                        },
                        "data": {
                            "id": user.id,
                            "email": user.email,
                            "username": user.username,
                        },
                    },
                    status=status.HTTP_200_OK,
                )
                
        else:
            return Response(
                {"success": False, "message": "Invalid Email or Password"},
                status=status.HTTP_400_BAD_REQUEST,
            )



class ForgotPasswordViewSet(ModelViewSet):
    queryset = User.objects.all().order_by("-id")
    permission_classes = [AllowAny]

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email,email_verified=True)
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": f"Email {email} is not registered before"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = generate_token(user.email, 60)
        recipient_email = user.email
        subject = "Reset assword link request from AgelessEatsKitchen.com"
        context = {"link": f"{config('HOST_URL')}reset-password/{token}/"}
        template="send_forgot_password_mail.html"
        mail_thread = threading.Thread(
            target=send_email_with_template, 
            args=(subject, recipient_email, template, context)
        )
        mail_thread.start()

        return Response(
            {"success": True, "message": f"Password reset link has been sent on {email}"},
            status=status.HTTP_200_OK,
        )



class ResetPasswordViewSet(ModelViewSet):
    queryset=User.objects.all()
    serializer_class=UserSerializer
    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        password = request.data.get("password")
        token=request.data.get('token')
        password2 = request.data.get("password2")

        if token is None:
            return Response(
                {"success": False, "message": "token is not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            payload = decode_token(token) # type: ignore
        except Exception:
            return Response(
                {"success": False, "message": "Link expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        print("payload",payload)
        if "email" not in payload:
            return Response(
                {"success": False, "message": "Invalid link"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email=payload["email"]).first()
        if not user:
            return Response(
                {"success": False, "message": "Email address not found"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if len(password) < 8 or len(password) > 14:
            return Response(
                {
                    "success": False,
                    "message": "Password length should be between 8 and 14 characters",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if password != password2:
            return Response(
                {"success": False, "message": "Passwords do not match"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(password)
        user.save()

        return Response(
            {"success": True, "message": f"Password changed successfully for {user.email}"},
            status=status.HTTP_200_OK,
        )



class ChangePasswordViewSet(ModelViewSet):
    queryset = User.objects.all().order_by("-id")
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        password = request.data.get("password")
        password2 = request.data.get("password2")

        if len(password) < 8 or len(password) > 14:
            return Response(
                {
                    "success": False,
                    "message": "Password length should be between 8 to 14",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if password != password2:
            return Response(
                {
                    "success": False,
                    "message": "password and Re-Password is not matching ",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=user_id)

        except Exception:
            return Response(
                {"success": False, "message": "Email is not Registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(password)
        user.save()

        return Response(
            {"success": True, "message": "Password changed successfully"},
            status=status.HTTP_200_OK,
        )


class LoginWithGoogleViewSet(ModelViewSet):
    queryset = User.objects.all()

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        token = request.data.get("token")
        if token:
            try:
                response = requests.get(
                    f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
                )

                if response.status_code == 200:
                    user_info = response.json()
                    print(user_info)

                    email = user_info["email"]
                    username = user_info["name"]
                    if username is None or username =="":
                        username=faker("username")
                        
                    username = ' '.join(username.split()).replace(' ', '_')
                    user = User.objects.filter(email=email)
                    print(user)
                    if user.exists():
                        user[0].is_active = True
                        user[0].save()
                        refresh_token = RefreshToken.for_user(user[0])
                        access_token = str(refresh_token.access_token)

                        return Response(
                            {
                                "success": True,
                                "message": "Google authentication Successfully done",
                                "token": {
                                    "access_token": access_token,
                                    "refresh_token": str(refresh_token),
                                },
                            },
                            status=status.HTTP_200_OK,
                        )

                    else:
                        user = User.objects.create(email=email, username=username)
                        user.is_active = True
                        user.set_password("password@123")
                        user.email_verified = True
                        user.save()
                        refresh_token = RefreshToken.for_user(user)
                        access_token = str(refresh_token.access_token)

                    # Process user info, create user, or authenticate user as needed
                    return Response(
                        {
                             "success": True,
                                "message": "Google authentication Successfully done",
                                "token": {
                                    "access_token": access_token,
                                    "refresh_token": str(refresh_token),
                                },
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
                    )

            except requests.exceptions.RequestException as e:
                return Response(
                    {"success": False, "message": "Something went wrong ! try again"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:
            return Response(
                {"success": False, "message": "Something went wrong ! Try again"},
                status=status.HTTP_400_BAD_REQUEST,
            )

