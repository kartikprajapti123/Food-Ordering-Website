from rest_framework import serializers
from orders.models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    subcategory_name = serializers.CharField(source="subcategory.name", read_only=True)

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
            'price',
            'order_item_total_price',
        ]

    def validate(self, data):
        if data.get('quantity') <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        if data.get('order_item_total_price') != data.get('price') * data.get('quantity'):
            raise serializers.ValidationError("Total price for the item is incorrect.")
        return data

class OrderSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)
    items = OrderItemSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'user_username',
            'customer_name',
            'order_number',
            'order_date',
            'status',
            'special_instructions',
            'delivery_address',
            'order_total_price',
            'deleted',
            'created_at',
            'updated_at',
            'items',
        ]

    def validate(self, data):
        if data.get('order_total_price') == "0":
            raise serializers.ValidationError("Order total price cannot be negative.")
    
        if data.get("delivery_address")==None or data.get("delivery_address").strip()=="":
            raise serializers.ValidationError("Delivery Address is required")
        if data.get("customer_name")==None or data.get("customer_name").strip()=="":
            raise serializers.ValidationError("Customer name is required")
        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)

        # Generate a unique order number
        order.order_number = f"ORD-{order.id:06d}"
        order.save()

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order

class OrderSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)
    items = OrderItemSerializer(many=True, required=False)
    order_number=serializers.CharField(required=False)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'user_username',
            'customer_name',
            'order_number',
            'order_date',
            'status',
            'special_instructions',
            'delivery_address',
            'order_total_price',
            'deleted',
            'created_at',
            'updated_at',
            'items',
        ]

    def validate(self, data):
        if data.get('order_total_price') == "0":
            raise serializers.ValidationError("Order total price cannot be negative.")
    
        if data.get("delivery_address") is None or data.get("delivery_address").strip() == "":
            raise serializers.ValidationError("Delivery Address is required")
        if data.get("customer_name") is None or data.get("customer_name").strip() == "":
            raise serializers.ValidationError("Customer name is required")
        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)

        # Generate a unique order number
        order.order_number = f"ORD-{order.id:06d}"
        order.save()

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        print(items_data)
        instance = super().update(instance, validated_data)

        # Track existing item IDs from the current order
        return instance


