from django.db import models
from user.models import User
from menukit.models import Category,SubCategory
from client.models import Client


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processed', 'Processed'),
        ('Delivered', 'Delivered'),
        ('Canceled', 'Canceled'),
    ]
    client=models.ForeignKey(Client,on_delete=models.CASCADE,related_name="order_client",null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # customer_name = models.CharField(max_length=50, null=True)
    order_number = models.CharField(max_length=50, unique=True)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=ORDER_STATUS_CHOICES, default="Pending", max_length=20)
    special_instructions = models.TextField(blank=True, null=True)
    delivery_date=models.DateField(blank=True,null=True)
    delivery_time=models.TimeField(blank=True,null=True)
    
    # delivery_address = models.CharField(max_length=100,blank=True, null=True)
    order_total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deleted = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.order_number} - {self.user.username}"
    class Meta:
        verbose_name="Manage Order"
        verbose_name_plural="Manage Orders"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items',null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    order_item_total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    deleted = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)
    def __str__(self):
        return f"Item in Order #{self.order.order_number}: {self.category.name if self.category else 'No Category'}"
    
    class Meta:
        verbose_name="Manage Kitchen"
        verbose_name_plural="Manage Kitchen"