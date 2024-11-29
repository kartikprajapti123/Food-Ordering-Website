from django.shortcuts import render

# Create your views here.
# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from menukit.models import Category,SubCategory
from menukit.serializers import CategorySerializer,SubCategorySerializer
from utils.pagination import mypagination
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.filter(deleted=0)
    serializer_class = CategorySerializer
    pagination_class = mypagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [SearchFilter, OrderingFilter]
    
    search_fields=[
        'id',
        'name',
        
    ]
    ordering_fields=[
        'id',
        'name'
    ]

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"success": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        serializer = self.serializer_class(instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"success": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        no_pagination = request.query_params.get("no_pagination")
        page_url=request.query_params.get("page_url")
        if page_url:
           queryset=queryset.filter(page_url=page_url)
        
        if no_pagination:
            print(queryset)
            serializer = self.serializer_class(queryset, many=True)
            print(serializer.data)
            return Response({"success": True, "data": serializer.data})

       

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(
                {"success": True, "data": serializer.data}
            )

        serializer = self.serializer_class(queryset, many=True)
        return self.get_paginated_response({"success": True, "data": serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted=1
        instance.save()# Perform a hard delete. Use soft delete if needed.
        return Response(
            {"success": True, "message": f"Menu {instance.name} deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
        
    @action(detail=False, methods=['get'], url_path='exclude-category')
    def exclude_category(self, request):
        category_id = request.query_params.get('categoryid', None)
        
        if not category_id:
            return Response(
                {"success": False, "message": "Category ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Exclude the category with the given category_id
            categories = Category.objects.filter(deleted=0).exclude(id=category_id)
            serializer = self.serializer_class(categories, many=True)
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_200_OK
            )
        except Category.DoesNotExist:
            return Response(
                {"success": False, "message": "Category not found."},
                status=status.HTTP_404_NOT_FOUND
            )



class SubCategoryViewSet(ModelViewSet):
    queryset = SubCategory.objects.filter(deleted=0)
    serializer_class = SubCategorySerializer
    pagination_class = mypagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [SearchFilter, OrderingFilter]
    
    search_fields=[
        'name',
        'category__name',
        'ingrediants',
        "price",
    ]
    ordering_fields=[
        'name',
        'category__name',
        'ingrediants',
        "price",
    ]

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"success": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        serializer = self.serializer_class(instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"success": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        no_pagination = request.query_params.get("no_pagination")
        category = request.query_params.get("category")
        

        page_url=request.query_params.get("page_url")
        
        if category:
           queryset=queryset.filter(category=category)
        if page_url:
           queryset=queryset.filter(page_url=page_url)
        
        if no_pagination:
            print(queryset)
            serializer = self.serializer_class(queryset, many=True)
            print(serializer.data)
            return Response({"success": True, "data": serializer.data})

       

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(
                {"success": True, "data": serializer.data}
            )

        serializer = self.serializer_class(queryset, many=True)
        return self.get_paginated_response({"success": True, "data": serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete=1 
        instance.save()# Perform a hard delete. Use soft delete if needed.
        return Response(
            {"success": True, "message": f"Menu SubCategory {instance.name} deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )




    @action(detail=False, methods=['post'],url_path="filter_subcategories",permission_classes=[IsAuthenticated])
    def filter_subcategories(self, request, *args, **kwargs):
        category_id = request.data.get('category_id')
        subcategory_id = request.data.get('subcategory_id')

        # Check if category_id and subcategory_id are provided
        if not category_id or not subcategory_id:
            return Response(
                {"success": False, "message": "category_id and subcategory_id are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch all subcategories for the given category_id, excluding the provided subcategory_id
        subcategories = SubCategory.objects.filter(category_id=category_id, deleted=0).exclude(id=subcategory_id)

        # Serialize the filtered subcategories
        serializer = self.serializer_class(subcategories, many=True)

        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK
        )