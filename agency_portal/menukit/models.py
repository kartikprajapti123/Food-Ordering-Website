from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    deleted=models.IntegerField(default=0)
    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    ingrediants=models.CharField(max_length=255,null=True)
    price=models.IntegerField(null=True)
    name = models.CharField(max_length=100)
    deleted=models.IntegerField(default=0)
    

    def __str__(self):
        return f"{self.category.name} - {self.name}"