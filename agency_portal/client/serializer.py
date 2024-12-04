from rest_framework import serializers
from .models import Client

class ClientSerializer(serializers.ModelSerializer):
    user_username=serializers.CharField(source="user.username",required=False)
    class Meta:
        model = Client
        fields = ['id', 'name', 'delivery_address','user','user_username']

    def validate(self, attrs):
        name = attrs.get("name")
        user = attrs.get("user")
        delivery_address = attrs.get("delivery_address")

        # Validate required fields
        if not name or name==0 or name=='0':
            raise serializers.ValidationError("Client name is required.")

        if not user:
            raise serializers.ValidationError("User is required.")

        if not delivery_address:
            raise serializers.ValidationError("Delivery address is required.")

        # Check for uniqueness of `name` per `user`
        if not self.instance:
            # When creating a new instance
            if Client.objects.filter(name=name, user=user).exists():
                raise serializers.ValidationError(
                    f"A client with the name '{name}' already exists for this user."
                )
        else:
            # When updating an existing instance
            if Client.objects.filter(name=name, user=user).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError(
                     f"A client with the name '{name}' already exists for this user."
                )

        return attrs
