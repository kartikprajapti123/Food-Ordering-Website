from rest_framework import serializers
from .models import Category, SubCategory

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
        
    def validate(self, attrs):
        name=attrs.get("name")
        if not self.instance:
            category_instance=Category.objects.filter(name=name)
            if category_instance.exists():
                raise serializers.ValidationError(f"Menu with this name '{name}' already exists")
            
        else:
            category_instance=Category.objects.filter(name=name).exclude(id=self.instance.id)
            if category_instance.exists():
                raise serializers.ValidationError(f"Menu with this name '{name}' already exists")
        return attrs
class SubCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = SubCategory
        fields = ['id', 'category', 'category_name', 'name', 'ingrediants',"price"]


    def validate(self, attrs):
        name=attrs.get("name")
        if not self.instance:
            subcategory_instance=SubCategory.objects.filter(name=name)
            if subcategory_instance.exists():
                raise serializers.ValidationError(f"Submenu with this name '{name}' already exists")
            
        else:
            subcategory_instance=SubCategory.objects.filter(name=name).exclude(id=self.instance.id)
            if subcategory_instance.exists():
                raise serializers.ValidationError(f"Submenu with this name '{name}' already exists")
            
        return attrs
        