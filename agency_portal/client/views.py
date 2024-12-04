from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from client.models import Client
from client.serializer import ClientSerializer
from utils.pagination import mypagination 
from rest_framework.decorators import action# Replace with your custom pagination if applicable
from user.models import User

class ClientViewSet(ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    pagination_class = mypagination  # Replace with your pagination class
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [SearchFilter, OrderingFilter]
    
    search_fields = ['name', 'delivery_address','user__username']
    ordering_fields = ['id','name', 'delivery_address','user__username']

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
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
        return Response(
            {"success": False, "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        no_pagination = request.query_params.get("no_pagination")

        if no_pagination:
            serializer = self.serializer_class(queryset, many=True)
            return Response({"success": True, "data": serializer.data})

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(
                {"success": True, "data": serializer.data}
            )

        serializer = self.serializer_class(queryset, many=True)
        return Response({"success": True, "data": serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"success": True, "message": f"Client '{instance.name}' deleted successfully."},
            status=status.HTTP_200_OK
        )
        
    @action(detail=False, methods=['get'], url_path='filter-by-username')
    def filter_by_username(self, request, *args, **kwargs):
        username = request.query_params.get('username')
        no_pagination=request.query_params.get("no_pagination")
        if not username:
            return Response(
                {"success": False, "message": "Username query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.filter(username=username).first()
        if not user:
            return Response(
                {"success": False, "message": f"No user found with username '{username}'."},
                status=status.HTTP_404_NOT_FOUND
            )

        clients = Client.objects.filter(user=user).order_by('-id')
        
        if no_pagination:
            serializer = self.serializer_class(clients, many=True)
            return Response({"success": True, "data": serializer.data})
        
        page = self.paginate_queryset(clients)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response({"success": True, "data": serializer.data})

        serializer = self.serializer_class(clients, many=True)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK
        )


    @action(detail=False, methods=['get'], url_path='get-delivery-address')
    def get_delivery_address(self, request, *args, **kwargs):
        name = request.query_params.get('name')
        user=request.user
        if not name:
            return Response(
                {"success": False, "message": "Name query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        client = Client.objects.filter(name=name,user=user).first()
        
        if not client:
            return Response(
                {"success": False, "message": f"No client found with name '{name}'."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Returning the delivery_address of the found client
        return Response(
            {
                "success": True,
                "data": {
                    "id":client.id,
                    "name": client.name,
                    "delivery_address": client.delivery_address
                }
            },
            status=status.HTTP_200_OK
        )
        
    @action(detail=False, methods=['get'], url_path='exclude-client-by-name')
    def exclude_client_by_name(self, request, *args, **kwargs):
        """
        This API will return all Client records except the one that matches the given 'name'.
        The request must be authenticated.
        """
        name = request.query_params.get('name')
        if not name:
            return Response(
                {"success": False, "message": "Name query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ensure the user is authenticated
        user = request.user

        # Filter clients where the user is the client owner and the name doesn't match the provided name
        clients = Client.objects.filter(user=user).exclude(name=name).order_by('-id')

        # Serialize the data
        serializer = self.serializer_class(clients, many=True)

        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK
        )