from django.urls import path
from render import views

urlpatterns = [
    path("",views.login,name="login"),
    path("register/",views.register,name="register"),
    path("change-password/",views.change_password,name="change_password"),
    path("forgot-password/",views.forgot_password,name="forgot_password"),
    path("reset-password/<str:token>/",views.reset_password,name="reset_password"),
    path("otp-verify/<str:token>/",views.otp_verify,name="otp-verify"),
    path("dashboard/",views.dashboard,name="dashboard"),
    path("edit-profile/",views.edit_profile,name="edit_profile"),
    path("support-ticket/",views.support_ticket,name="support_ticket"),
    path("create-order/",views.create_order,name="create_order"),
    path("view-order/<str:order_id>/",views.view_order,name="view_order"),
    path("myorder/",views.myorders,name="myorders"),
    path("update-order/<str:id>/",views.update_order,name="update_order"),
    path("myclient/",views.myclient,name="myclient"),

    
    
    

    
    
    
    
]
