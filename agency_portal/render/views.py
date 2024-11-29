from django.shortcuts import render

# Create your views here.
def login(request):
    return render(request,"login.html")


def register(request):
    return render(request,"register.html")



def change_password(request):
    return render(request,"mychangepassword.html")

def reset_password(request,token):
    return render(request,"reset-password.html")

def forgot_password(request):
    return render(request,"forgot-password.html")

def otp_verify(request,token):
    return render(request,"verification-code.html")


def dashboard(request):
    return render(request,"dashboard.html")

def edit_profile(request):
    return render(request,"myprofileedit.html")

def support_ticket(request):
    return render(request,"support-tickets.html")



def create_order(request):
    return render(request,"create-order.html")


def view_order(request,order_id):
    return render(request,"view-order.html")



def myorders(request):
    return render(request,"myorders.html")


def update_order(request,id):
    return render(request,"update-order.html")