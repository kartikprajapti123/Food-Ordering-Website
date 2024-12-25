from rest_framework import serializers
from orders.models import Order, OrderItem
from client.models import Client
from decouple import config
from threading  import Thread

from utils.send_mail import send_email_with_template
class OrderItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    subcategory_name = serializers.CharField(source="subcategory.name", read_only=True)
    special_request=serializers.CharField(allow_blank=True,required=False)
    class Meta:
        model = OrderItem
        fields = [
            'id',
            'order',
            'category',
            'subcategory',
            'category_name',
            'subcategory_name',
            'quantity',
            "special_request",
            'price',
            'order_item_total_price',
        ]

    def validate(self, data):
        if data.get('quantity') <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        # if data.get('order_item_total_price') != data.get('price') * data.get('quantity'):
            # raise serializers.ValidationError("Total price for the item is incorrect.")
        return data

class OrderSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)
    items = OrderItemSerializer(many=True, required=False)
    order_number=serializers.CharField(required=False)
    client_name=serializers.CharField(source="client.name",required=False)
    client_delivery_address=serializers.CharField(source="client.delivery_address",required=False)
    delivery_date = serializers.DateField(required=False, allow_null=True)
    delivery_time = serializers.TimeField(required=False, allow_null=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'user_username',
            'client',
            'client_name',
            'client_delivery_address',
            'order_number',
            'order_date',
            'status',
            'order_total_price',
            'delivery_date',
            'delivery_time',
            'deleted',
            'created_at',
            'updated_at',
            'items',
        ]

    def validate(self, data):
        if data.get('client') == None:
            raise serializers.ValidationError("Client is required.")
    
        if data.get('order_total_price') == "0":
            raise serializers.ValidationError("Order total price cannot be negative.")
    
        if data.get("delivery_date")==None:
            raise serializers.ValidationError("Delivery date is required")
            
        if data.get("delivery_time")==None:
            raise serializers.ValidationError("Delivery time is required")
            
        if data.get("items")==[]:
            raise serializers.ValidationError("Order item is required")
            
        # if data.get("delivery_address") is None or data.get("delivery_address").strip() == "":
            # raise serializers.ValidationError("Delivery Address is required")
        # if data.get("customer_name") is None or data.get("customer_name").strip() == "":
            # raise serializers.ValidationError("Customer name is required")
        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        
        order = Order.objects.create(**validated_data)
        # Generate a unique order number
        order.order_number = f"ORD-{order.id:06d}"
        order.save()

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            
            
        
        subject=f"New Order has been created by {order.user.username}"
        to="orders@agelesseatskitchen.com"
        template="send_order_email.html"
        context={
            "order_number":order.order_number,
            "order_date":order.order_date,
            "order_status":order.status,
            "delivery_date":order.delivery_date,
            "order_total_price":order.order_total_price,
            "order_link":"https://www.agelesseatskitchen.com/admin/orders/order/",
            "order_items":order.items.all(),
    
        } 
        
        # send_email_with_template(subject=subject,recipient_email=to,template_name="send_order_email.html",context=context)
        email=Thread(target=send_email_with_template,args=(subject,to,template,context))
        email.start()
        
        
        subject=f"{order.order_number} New Order has been Successfully Created"
        to=f"{order.user.email}"
        template="send_email_to_creator.html"
        context={
            "username":f"{order.user.username}",
            "order_number":order.order_number,
            "order_date":order.order_date,
            "order_status":order.status,
            "delivery_date":order.delivery_date,
            "order_total_price":order.order_total_price,
            "order_link":f"https://www.agelesseatskitchen.com/view-order/{order.id}/",
            "order_items":order.items.all(),
            
            
        } 
        
        # send_email_with_template(subject=subject,recipient_email=to,template_name="send_order_email.html",context=context)
        email=Thread(target=send_email_with_template,args=(subject,to,template,context))
        email.start()
        
        
        return order
    
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        print(items_data)
        instance = super().update(instance, validated_data)

        # Track existing item IDs from the current order
        return instance


