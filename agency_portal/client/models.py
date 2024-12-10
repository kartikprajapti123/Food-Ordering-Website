from django.db import models
from user.models import User
# from django.db.models import _ 
from django.utils.translation import gettext as _
# Create your models here.
class Client(models.Model):
    name=models.CharField(verbose_name=_("Client Name"),max_length=100)
    delivery_address=models.CharField(verbose_name=_("Client Delivery Address"),max_length=100)
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='client_name',verbose_name=_("Agency"),null=True)
    
    class Meta:
        verbose_name = 'Manage Client'
        verbose_name_plural = 'Manage Clients'
    def __str__(self):
        return self.name
    
