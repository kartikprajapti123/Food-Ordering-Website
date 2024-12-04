import threading
from django.shortcuts import render

# Create your views here.
# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from support_ticket.models import Attachment, Support_ticket
from support_ticket.serializers import AttachmentSerializer, SupportTicketSerializers
from utils.pagination import mypagination
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.mail import send_mail
from decouple import config
from django.db import transaction

from django.core.mail import send_mail
from django.template.loader import render_to_string

from utils.send_mail import send_email_with_template

class SupportTicketPagesViewSet(ModelViewSet):
    queryset = Support_ticket.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = SupportTicketSerializers
    pagination_class = mypagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [SearchFilter, OrderingFilter]

    search_fields = [
        "ticket_id",
        "user__username",
        "priority",
        "category",
        "description",
    ]
    ordering_fields = [
        "id",
        "ticket_id",
        "user__username",
        "priority",
        "category",
        "description",
    ]

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data, context={"request": request})

        if serializer.is_valid():
            with transaction.atomic():
                instance = serializer.save()


                subject = f" Ticket ID:{instance.ticket_id} in {config("WEB_URL")}"
                to = config("SEND_EMAIL")
                context = {
                    "title": instance.title, "description": instance.description
                }
                # send_email_verfication(subject=subject, to=to, context=context)
                # subject, recipient_email, template_name, context
                email_thread = threading.Thread(
                    target=send_email_with_template, args=(subject, to, "send_support_ticket_email.html",context)
                )
                email_thread.start()
                # # Prepare email content from template
                # context = {"title": instance.title, "description": instance.description}
                # html_content = render_to_string("ticket_email.html", context)
    
                # send_mail(
                #     f"[Ticket ID: {instance.ticket_id}] - {instance.title}",
                #     instance.description,  # Plain text version
                #     config("SEND_EMAIL"),
                #     # ["kartikprajapati26122004@gmail.com",],
                #     ["accessjerry1@gmail.com"],

                #     fail_silently=False,
                #     html_message=html_content,  # HTML content from template
                # )
                
                

                return Response(
                    {"success": True, "data": serializer.data},
                    status=status.HTTP_201_CREATED,
                )
        else:
            return Response(
                {"success": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        serializer = self.serializer_class(instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"success": False, "message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        no_pagination = request.query_params.get("no_pagination")
        page_url = request.query_params.get("page_url")
        print(page_url)
        if page_url:
            queryset = queryset.filter(page_url=page_url)

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
        print("called")
        instance = self.get_object()
        instance.delete()  # Perform a hard delete. Use soft delete if needed.
        return Response(
            {"success": True, "message": "Page deleted successfully."},
            status=status.HTTP_200_OK,
        )
