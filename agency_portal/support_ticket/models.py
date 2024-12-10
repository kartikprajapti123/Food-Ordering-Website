from django.db import models

# Create your models here.
from user.models import User
from django.utils.translation import gettext as _

class Support_ticket(models.Model):
    priority_choices = [
        ("High", "High"),
        ("Medium", "Medium"),
        ("Low", "Low"),
    ]
    status_choices = [
        ("Open", "Open"),
        ("InProgress", "InProgress"),
        ("Closed", "Closed"),
    ]
    CATEGORY_CHOICES = [
        ("Technical", "Technical"),            
        ("Billing", "Billing"),                
        ("Account", "Account"),                
        ("General", "General"),                
    ]
    title=models.CharField(max_length=100,null=True)
    ticket_id = models.CharField(max_length=50, unique=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="user_supoort_ticket",verbose_name=_("Agency"))
    # subject = models.CharField(max_length=255)
    priority = models.CharField(choices=priority_choices, max_length=100, default="Low")
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=100, default="General",verbose_name=_("Ticket Category"))
    status=models.CharField(choices=status_choices,default="Open")
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ticket_id} - {self.title} "
    
    class Meta:
        verbose_name="Manage Support Ticket"
        verbose_name_plural="Manage Support Tickets"

class Attachment(models.Model):
    support_ticket = models.ForeignKey(Support_ticket, related_name="attachments", on_delete=models.CASCADE)
    file = models.FileField(upload_to="support_ticket/")

    def __str__(self):
        return f"Attachment for {self.support_ticket.ticket_id}"
