from django.db import models
from django.utils.translation import gettext as _

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True,verbose_name=_("Menu Name"))
    deleted = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Manage Menu"  # Display "Menu" instead of "Category"
        verbose_name_plural = "Manage Menus"  # Display "Menus" instead of "Categories"
        
    def __str__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=100,verbose_name=_("SubMenu Name"))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories',verbose_name=_("Menu Name"))
    price = models.FloatField(null=True,verbose_name=_("SubMenu Price"))
    deleted = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Manage SubMenu"  # Display "SubMenu" instead of "SubCategory"
        verbose_name_plural = "Manage SubMenus"  # Display "SubMenus" instead of "SubCategories"

    def __str__(self):
        return f"{self.category.name} - {self.name}"
