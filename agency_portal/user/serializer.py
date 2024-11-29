from rest_framework import serializers
from user.models import User
from utils.generate_otp import generate_otp

class UserSerializer(serializers.ModelSerializer):
    email=serializers.CharField(required=True)
    class Meta:
        model=User
        fields=[
            'id',
            "username",
            'email',
            "profile_picture",
            'email_verified',
            'otp'
        ]
        
    def validate(self, attrs):
        email=attrs.get("email")
        username=attrs.get("username")
        
            
        if self.instance:
            user_username_instanse=User.objects.filter(username=username,email_verified=True).exclude(id=self.instance.id)
        if user_username_instanse.exists():
            raise serializers.ValidationError("Username already exists")
        
        if self.instance:
            user_email_instanse=User.objects.filter(email=email,email_verified=True).exclude(id=self.instance.id)
        if user_email_instanse.exists():
            raise serializers.ValidationError("Email Address already exists")
        
        return attrs
        
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
        
class RegisterSerializer(serializers.ModelSerializer):
    password2=serializers.CharField(required=False)
    email=serializers.CharField(required=True)
    class Meta:
        model=User
        fields=[
            'username',
            'email',
            "password",
            "password2",
            "profile_picture",
            
            'otp',
        ]
        
    def validate(self, attrs):
        email=attrs.get("email")
        username=attrs.get("username")
        password=attrs.get("password")
        password2=attrs.get("password2")
        
        
        user_username_instanse=User.objects.filter(username=username,email_verified=True)
        if user_username_instanse.exists():
            raise serializers.ValidationError("Username already exists")
        
        user_email_instanse=User.objects.filter(email=email,email_verified=True)
        if user_email_instanse.exists():
            raise serializers.ValidationError("Email Address already exists")
        
        if password and (len(password) < 8 or len(password) > 14):
            raise serializers.ValidationError("Password length should be between 8 to 14 characters.")
        
        if password and password2 and password != password2:
            raise serializers.ValidationError("Password and Re-Password is not matching.")
        

        return attrs
    
    def create(self, validated_data):
        password2=validated_data.pop('password2')
        password=validated_data.pop('password')
        
        user=User.objects.create(**validated_data)
        user.otp=generate_otp()
        
        user.is_active=True
        
        user.set_password(password)
        
        user.save()
        
        return user
    

class OtpSerilaizer(serializers.Serializer):
    email=serializers.CharField(required=True)
    otp=serializers.CharField(required=True)
    