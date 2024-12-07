from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    deleted = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Manage Menu"  # Display "Menu" instead of "Category"
        verbose_name_plural = "Manage Menus"  # Display "Menus" instead of "Categories"
        
    def __str__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories',verbose_name="Menu")
    price = models.FloatField(null=True)
    ingrediants = models.CharField(max_length=255, null=True,blank=True,default="")
    deleted = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Manage SubMenu"  # Display "SubMenu" instead of "SubCategory"
        verbose_name_plural = "Manage SubMenus"  # Display "SubMenus" instead of "SubCategories"

    def __str__(self):
        return f"{self.category.name} - {self.name}"
