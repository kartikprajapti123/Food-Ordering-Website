from rest_framework import serializers
from support_ticket.models import Support_ticket, Attachment
import random

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = [
            "id",
            "support_ticket",
            "file"
        ]

class SupportTicketSerializers(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)
    user_profile_picture = serializers.CharField(source="user.profile_picture", read_only=True)
    attachments = AttachmentSerializer(many=True, required=False, read_only=True)  # Attachments should be read-only here
    ticket_id = serializers.CharField(required=False)
    
    class Meta:
        model = Support_ticket
        fields = [
            "id",
            "ticket_id",
            "user",
            "title",
            "user_username",
            "user_profile_picture",
            "priority",
            "attachments",
            "status",
            "category",
            "description",
            "created_at",
            "updated_at",
        ]
        
    def validate(self, attrs):
        print(attrs)
        title=attrs.get("title")
        description=attrs.get("description")
        print(len(description))
        request = self.context.get('request')
        attachment = request.FILES.getlist('attachments')
        print(attachment)
        if title is None:
            raise serializers.ValidationError("Title is required")
        
        elif not attachment:  # Check if attachment is empty
            raise serializers.ValidationError("Attachment: At least one file is required")
          
        
        return attrs
            
    def generate_ticket_id(self):
        
        # Generate a 4-digit random number as the ticket ID
        return f"TICKET-{random.randint(1000, 9999)}"
    
    def create(self, validated_data):
        # Generate the ticket ID
        validated_data["ticket_id"] = self.generate_ticket_id()
        
        # Handle attachments from request.FILES
        attachments_data = self.context['request'].FILES.getlist('attachments')  # Retrieve file list
        
        # Create support ticket
        support_ticket_instance = Support_ticket.objects.create(**validated_data)
        print(attachments_data)
        # Save each attachment
        for file in attachments_data:
            print(file)
            Attachment.objects.create(support_ticket=support_ticket_instance, file=file)
        
        return support_ticket_instance
    
    def to_representation(self, instance):
        # Customize the representation
        support_ticket = super().to_representation(instance)
        support_ticket['attachments'] = AttachmentSerializer(instance.attachments.all(), many=True).data
        return support_ticket
