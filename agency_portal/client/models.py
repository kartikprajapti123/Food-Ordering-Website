from django.db import models
from user.models import User
# Create your models here.
class Client(models.Model):
    name=models.CharField(max_length=100)
    delivery_address=models.CharField(max_length=100)
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='client_name',null=True)
    
    class Meta:
        verbose_name = 'Manage Client'
        verbose_name_plural = 'Manage Clients'
    def __str__(self):
        return self.name
    
