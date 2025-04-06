import threading
from django.core.mail import EmailMessage
from django.utils.timezone import localtime
from argparse import Action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from orders.models import Order, OrderItem
from orders.serializers import OrderSerializer, OrderItemSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from utils.pagination import mypagination
from django.utils.timezone import now
from menukit.models import Category,SubCategory
from datetime import timedelta
from rest_framework.decorators import action
from datetime import datetime
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.http import HttpResponse
from io import BytesIO

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.filter(deleted=False).order_by("id")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    pagination_class = mypagination

    authentication_classes = [JWTAuthentication]

    search_fields = [
        "user__username",
        "items__category__name",
        "items__subcategory__name",
            'client__name',
            'client__delivery_address',
        "order_number",
        "order_date",
        "status",
        'delivery_date',
            'delivery_time',
        "order_total_price",
        "deleted",
        "created_at",
        "updated_at",
    ]
    ordering_fields = [
        "user__username",
        "items__category__name",
        "items__subcategory__name",
            # 'customer_name',
            'client__name',
            'client__delivery_address',
        "order_number",
        'delivery_date',
            'delivery_time',
        "order_date",
        "status",
        "order_total_price",
        "deleted",
        "created_at",
        "updated_at",
    ]

    def create(self, request, *args, **kwargs):
        data = request.data
        if data.get("user") == None:
            data["user"] = request.user.id
        serializer = self.serializer_class(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"success": False, "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        if not request.user.is_superuser or request.user.id == serializer.data.get(
            "user"
        ):
            return Response(
                {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "success": False,
                    "message": "You are not an 'Admin' or the Owner of this Order.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        data_list = request.data.get("items", [])
        print(data_list)

        # Set the user field if it's not provided
        if data.get("user") is None:
            data["user"] = request.user.id

        # Initialize the serializer and validate the incoming data
        serializer = self.serializer_class(instance=instance, data=data, partial=True)

        if serializer.is_valid():
            # Save the updated order instance
            instance = serializer.save()

            # Process the items (order items)
            if len(data_list) > 0:
                for item_data in data_list:

                    item_id = item_data.get('id')

                    if item_id:
                        # Try to get the existing OrderItem and update it
                        try:
                            orderitem = OrderItem.objects.get(id=item_id, order=instance)
                        except OrderItem.DoesNotExist:
                            return Response(
                                {
                                    "success": False,
                                    "data": f"OrderItem with this id {item_id} does not exist.",
                                },
                                status=status.HTTP_200_OK,
                            )

                        # Update the existing OrderItem fields
                        category_instance = Category.objects.get(id=item_data['category'])  # Get Category instance
                        subcategory_instance = SubCategory.objects.get(id=item_data['subcategory'])  # Get Category instance
                        
                        orderitem.category = category_instance
                        orderitem.quantity =item_data['quantity']
                        orderitem.subcategory = subcategory_instance
                        orderitem.special_request = item_data["special_request"]
                        
                        orderitem.order_item_total_price = item_data['order_item_total_price']
                        orderitem.order = instance  # Ensure the order field is correctly linked

                        orderitem.save()

                    else:
                        # Create a new OrderItem
                        try:
                            category_instance = Category.objects.get(id=item_data['category'])
                            subcategory_instance = SubCategory.objects.get(id=item_data['subcategory'])
                            
                        except Order.DoesNotExist:
                            return Response(
                                {"success": False, "message": "Order does not exist."},
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                        except Category.DoesNotExist:
                            return Response(
                                {"success": False, "message": "Category does not exist."},
                                status=status.HTTP_400_BAD_REQUEST,
                            )

                        # Create a new OrderItem instance
                        OrderItem.objects.create(
                            order=instance,
                            category=category_instance,
                            subcategory=subcategory_instance,
                            quantity=item_data['quantity'],
                            order_item_total_price=item_data['order_item_total_price'],
                            price=item_data['price']
                        )

            # Return success response with updated order data
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_200_OK,
            )

        # If the serializer is not valid, return error response
        return Response(
            {"success": False, "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())
        queryset=queryset.order_by("-id")
        no_pagination = request.query_params.get("no_pagination")
        page_url = request.query_params.get("page_url")
        status = self.request.query_params.get("status")
        time_period = self.request.query_params.get("time_period")
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        username = self.request.query_params.get("username")
        

        if username:
            queryset = queryset.filter(user__username=username)
            
        if page_url:
            queryset = queryset.filter(page_url=page_url)

        if no_pagination:
            serializer = self.serializer_class(queryset, many=True)
            print(serializer.data)
            return Response({"success": True, "data": serializer.data})

        if status:
            queryset = queryset.filter(status=status)

        # Filter by time period
        if time_period:
            today = now().date()
            if time_period == "last_week":
                queryset = queryset.filter(order_date__gte=today - timedelta(weeks=1))
            elif time_period == "last_month":
                queryset = queryset.filter(order_date__gte=today - timedelta(days=30))
            elif time_period == "last_year":
                queryset = queryset.filter(order_date__gte=today - timedelta(days=365))

        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            queryset = queryset.filter(order_date__gte=start_date)

        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            queryset = queryset.filter(order_date__lte=end_date)

        status_order = {
            "Pending": 1,
            "Processed": 2,
            "Delivered": 3,
            "Canceled": 4,
        }
        # queryset = sorted(
            # queryset,
            # key=lambda x: status_order.get(
                # x.status, 5
            # ),  # Default to 5 if status is not in the list
        # )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(
                {"success": True, "data": serializer.data}
            )

        serializer = self.serializer_class(queryset, many=True)
        return self.get_paginated_response({"success": True, "data": serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = "Canceled"  # Soft delete
        instance.save()
        return Response(
            {"success": True, "message": "Order successfully canceled."},
            status=status.HTTP_200_OK,
        )
        
        
    def send_email_with_receipt(self, email, pdf_content, filename):
        msg = EmailMessage(
            subject="Your Order Receipt",
            body="Please find your receipt attached.",
            to=[email],
        )
        msg.attach(filename, pdf_content, "application/pdf")
        msg.send()

    @action(detail=False, methods=["GET"], url_path="generate-reciept", permission_classes=[AllowAny])
    def generate_reciept(self, request, *args, **kwargs):
        order_id = request.query_params.get("id")
        try:
            order_instance = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'success': False, "message": f"Order with id {order_id} does not exist"})

        if order_instance.status.lower() != "delivered":
            return Response({'success': False, "message": "Order is not delivered yet. Receipt cannot be generated."})

        order_data = {
            "order_number": order_instance.order_number,
            "client": order_instance.client.name if order_instance.client else "N/A",
            "agency": order_instance.user.username,
            "order_date": localtime(order_instance.order_date).strftime("%Y-%m-%d %H:%M"),
            "delivery_date": order_instance.delivery_date.strftime("%Y-%m-%d") if order_instance.delivery_date else "N/A",
            "delivery_time": order_instance.delivery_time.strftime("%H:%M") if order_instance.delivery_time else "N/A",
            "order_total_price": str(order_instance.order_total_price),
        }

        item_list = []
        for item in order_instance.items.all():
            item_list.append({
                "menu_name": item.category.name if item.category else "N/A",
                "submenu_name": item.subcategory.name if item.subcategory else "N/A",
                "quantity": item.quantity,
                "price": str(item.price),
                "total_price": str(item.order_item_total_price),
                "special_request": item.special_request or "",
            })

        # Render HTML
        html_string = render_to_string("receipt_template.html", {
            "order": order_data,
            "items": item_list,
        })

        # Generate PDF
        result = BytesIO()
        pisa_status = pisa.CreatePDF(html_string, dest=result)

        if pisa_status.err:
            return Response({'success': False, 'message': 'Failed to generate PDF'}, status=500)

        # Send email in a separate thread
        pdf_bytes = result.getvalue()
        user_email = order_instance.user.email
        pdf_filename = f"receipt_{order_instance.order_number}.pdf"
        threading.Thread(target=self.send_email_with_receipt, args=(user_email, pdf_bytes, pdf_filename)).start()

        return Response({'success': True, 'message': f'Receipt sent to your mail address:- {user_email}'})
    
    @action(detail=False, methods=['post'], url_path='create-order')
    def create_order(self, request):
        user = request.user
        today = now().date()
        start_of_week = today - timedelta(days=today.weekday()) 
        end_of_week = start_of_week + timedelta(days=6)  
        
        weekly_orders = Order.objects.filter(
            user=user,
            order_date__date__gte=start_of_week,
            order_date__date__lte=end_of_week
        ).count()

        # if weekly_orders >= 2:
            # return Response(
                # {"success":False,"message": "You have already created 2 orders this week. Please try again next week."},
                # status=status.HT/TP_400_BAD_REQUEST
            # )

        return Response(
            {"success":True,"message":"User Can do Order"},
            status=status.HTTP_201_CREATED
        )

    @action(detail=False,methods=['POST',],url_path="status-update")
    def status_update(self,request,*args, **kwargs):
        data=request.data 
        if data.get("id")==None:
            return Response(
            {"success": False, "message": "Order Is is required"},
            status=status.HTTP_400_BAD_REQUEST,
        ) 
        order_instance=Order.objects.get(id=data.get("id"))
        order_instance.status=data.get("status")
        order_instance.save()
        return Response(
            {"success": True, "message": "Order status Updated"},
            status=status.HTTP_200_OK,
        ) 

class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.filter(deleted=0)
    serializer_class = OrderItemSerializer
    pagination_class = mypagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [SearchFilter, OrderingFilter]

    search_fields = [
        "order",
        "category",
        "subcategory",
        "category_name",
        "subcategory_name",
        "quantity",
        "price",
        "order_item_total_price",
    ]
    ordering_fields = [
        "order",
        "category",
        "subcategory",
        "category_name",
        "subcategory_name",
        "quantity",
        "price",
        "order_item_total_price",
    ]

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"success": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        serializer = self.serializer_class(instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"success": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        no_pagination = request.query_params.get("no_pagination")
        page_url = request.query_params.get("page_url")
        
        if page_url:
            queryset = queryset.filter(page_url=page_url)

        if no_pagination:
            print(queryset)
            serializer = self.serializer_class(queryset, many=True)
            print(serializer.data)
            return Response({"success": True, "data": serializer.data})

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(
                {"success": True, "data": serializer.data}
            )

        serializer = self.serializer_class(queryset, many=True)
        return self.get_paginated_response({"success": True, "data": serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"success": True, "message": f"Order Item deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
