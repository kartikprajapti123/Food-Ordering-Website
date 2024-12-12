import tempfile
import os
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from io import BytesIO
import io
import zipfile
from django.contrib.admin import RelatedFieldListFilter,RelatedOnlyFieldListFilter
from django.contrib.admin import SimpleListFilter
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.contrib import admin
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)
from django.http import Http404
from menukit.models import Category, SubCategory
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from user.models import User
from orders.models import Order, OrderItem
from support_ticket.models import Support_ticket, Attachment
from django.contrib.auth.models import Group
import os
from client.models import Client
from django.shortcuts import get_object_or_404
from django.contrib import admin
from django.contrib.admin import AdminSite
from rest_framework_simplejwt.token_blacklist import models

from django.utils.safestring import mark_safe
from django.template.loader import (
    render_to_string,
)  # Unregister Blacklisted and Outstanding tokens
from django.urls import path, reverse
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.conf import settings
from orders.models import Order
import os
from django.conf import settings
import os
import imgkit
from django.core.exceptions import ImproperlyConfigured
from django.http import QueryDict
from django.urls import reverse
from io import BytesIO
from zipfile import ZipFile
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime


class CustomAdminSite(AdminSite):
    site_header = (
        "AgelessEatsKitchen.com Admin"  # Custom header text for the admin panel
    )
    site_title = "AgelessEatsKitchen Admin"  # Title text in the browser tab
    index_title = "Welcome to AgelessEatsKitchen Admin"  # Title for the index page in the admin panel


from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
import os

# Register the custom admin site
admin.site = CustomAdminSite()


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "deleted")  # Display columns
    search_fields = ("name",)  # Search bar
    list_filter = ("deleted",)  # Filter by 'deleted' field
    ordering = ("name",)  # Default ordering



class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "deleted")  # Display columns
    search_fields = ("name", "category__name")  # Search bar with category name support
    list_filter = (
        ('category', RelatedOnlyFieldListFilter),  # Correct filter for category
    )  
  # Correct way to add the filter class
    ordering = ("category", "name")  # Default ordering
    autocomplete_fields = ("category",)  # Autocomplete for category selection

    # def get_search_results(self, request, queryset, search_term):
        # return queryset

    # def get_queryset(self, request):
        # qs = super().get_queryset(request)
        # return qs.select_related("category")
    
class OrderItemInline(admin.TabularInline):
    """
    Inline admin to display OrderItem details within the Order panel.
    """

    model = OrderItem
    extra = 0
    fields = ("category_name", "subcategory_name", "quantity", "price", "order_item_total_price")
    readonly_fields = ("category_name", "subcategory_name", "quantity", "price", "order_item_total_price",)
    # autocomplete_fields = ("category", "subcategory")

    def get_readonly_fields(self, request, obj=None):
        """
        Ensure all fields in OrderItem are read-only in the inline.
        """
        return self.fields if obj else super().get_readonly_fields(request, obj)

    def has_add_permission(self, request, obj=None):
        """
        Disable adding new OrderItems in the inline.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Disable deleting OrderItems in the inline.
        """
        return False

    # Custom methods to display category and subcategory names as text (without links)
    def category_name(self, obj):
        return obj.category.name if obj.category else "N/A"
    
    def subcategory_name(self, obj):
        return obj.subcategory.name if obj.subcategory else "N/A"

    category_name.short_description = "Menu Name"  # Custom label for display
    subcategory_name.short_description = "Submenu Name"  # Custom label for display



class OrderAdmin(admin.ModelAdmin):
    """
    Admin panel for managing Orders, with the 'status' field editable.
    """

    inlines = [OrderItemInline]
    list_display = (
        "order_number",
        "user",
        "status",
        "get_client_name",
        "order_total_price",
        "order_date",
        "delivery_date",
        "delivery_time",
    )
    list_filter = ("status", "order_date", ("user",RelatedOnlyFieldListFilter))
    search_fields = (
        "order_number",
        "delivery_date",
        "delivery_time",
        "user__username",
        "client__name",
        "client__delivery_address",
        
    )
    ordering = ("-order_date",)
    list_editable = ("status",)
    date_hierarchy = "order_date"
    readonly_fields = (
        "user",
        "client",
        "get_client_name",
        "get_client_delivery_address",
        "order_number",
        "order_date",
        
        "special_instructions",
        "deleted",
        "delivery_date",
        "delivery_time",
        "created_at",
        "updated_at",
        "order_total_price",
    )

    class Media:
        js = ("admin/js/total_amount.js",)
        
    change_form_template = "admin/orders/Order/change_form.html"
    change_list_template = "admin/orders/Order/change_list.html"
    
    

    def get_client_name(self, obj):
        return obj.client.name if obj.client else None

    get_client_name.short_description = "Client Name"

    def get_client_delivery_address(self, obj):
        return obj.client.delivery_address if obj.client else None

    get_client_delivery_address.short_description = "Client Delivery Address"

    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     """
    #     Override the change view to add order_total_price below inlines.
    #     """
    #     extra_context = extra_context or {}
    #     order = self.model.objects.get(pk=object_id)
    #     total_price_html = render_to_string('admin/order_total_price.html', {'order': order})
    #     extra_context['after_inlines'] = mark_safe(total_price_html)
    #     return super().change_view(request, object_id, form_url, extra_context)

    def has_add_permission(self, request):
        return False

    # def has_delete_permission(self, request, obj=None):
        # return False

    def generate_report(self, request):
        """ 
        Generate separate professionally formatted PDF reports for each user,
        summarizing total quantities of items across all orders without pricing.
        """
        try:
            # Start with the filtered queryset based on current admin filters
            queryset = self.get_queryset(request)

            # Further filter the queryset if specific IDs are provided
            selected_ids = request.GET.getlist("ids")
            if selected_ids:
                queryset = queryset.filter(id__in=selected_ids)

            # Apply additional filters from the request (e.g., status__exact)
            filter_params = {key: value for key, value in request.GET.items() if key != "ids"}
            if filter_params:
                queryset = queryset.filter(**filter_params)

            # Fetch the filtered orders and related items
            orders = queryset.prefetch_related("items", "client")

            if not orders.exists():
                return HttpResponse("No orders data found to generate Order.", status=400)

            # Group orders by user
            user_orders = {}
            for order in orders:
                user = order.user  # Assuming 'user' field in 'client'
                if user not in user_orders:
                    user_orders[user] = []
                user_orders[user].append(order)

            # Prepare a buffer to store PDFs
            buffer = BytesIO()

            for user, orders in user_orders.items():
                pdf_buffer = BytesIO()
                doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)

                # Content container
                elements = []
                styles = getSampleStyleSheet()

                # Add Agency/Report Title
                title = Paragraph(f"<strong>Agency Report: {user.username}</strong>", styles["Title"])
                elements.append(title)
                elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%b %d, %Y')}", styles["Normal"]))
                elements.append(Paragraph(f"<strong>User Details:</strong> {user.username}", styles["Normal"]))
                elements.append(Paragraph(f"Email: {user.email}", styles["Normal"]))
                elements.append(Paragraph("<br/><br/>", styles["Normal"]))

                # Table Header for Orders Summary
                data = [["Order Number", "Order Date", "Client Name"]]
                for order in orders:
                    data.append([
                        order.order_number,
                        order.order_date.strftime('%b %d, %Y'),
                        order.client.name,
                    ])

                # Add Orders Table
                table = Table(data, colWidths=[100, 100, 150])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(table)
                elements.append(Paragraph("<br/><br/>", styles["Normal"]))

                # Summarize Total Quantities by Subcategory
                item_summary = {}
                for order in orders:
                    for item in order.items.all():
                        if item.subcategory not in item_summary:
                            item_summary[item.subcategory] = 0
                        item_summary[item.subcategory] += item.quantity

                # Add Item Summary Table
                summary_data = [["Subcategory", "Total Quantity"]]
                for subcategory, total_quantity in item_summary.items():
                    summary_data.append([subcategory, total_quantity])

                summary_table = Table(summary_data, colWidths=[300, 100])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(Paragraph("<strong>Order Item Summary:-</strong>", styles["Heading2"]))
                elements.append(summary_table)

                # Build PDF
                doc.build(elements)
                pdf_buffer.seek(0)

                # Add the generated PDF to the main buffer
                buffer.write(pdf_buffer.read())

            # Return the response as a downloadable PDF report
            buffer.seek(0)
            response = HttpResponse(buffer, content_type="application/pdf")
            response["Content-Disposition"] = f"attachment; filename={user}_agency_report.pdf"
            return response

        except Exception as e:
            return HttpResponse(f"An error occurred while generating the report: {e}", status=500)
    def changelist_view(self, request, extra_context=None):
        """
        Add a custom button for generating a report in the changelist view.
        """
        extra_context = extra_context or {}

        # Get the filtered queryset based on current admin filters
        queryset = self.get_queryset(request)
        # Serialize the IDs of only the filtered queryset
        filtered_ids = list(queryset.values_list("id", flat=True))
        query_dict = QueryDict(mutable=True)
        query_dict.setlist("ids", filtered_ids)

        # Include all other filters from the current request
        for key, value in request.GET.items():
            if key != "ids":  # Avoid overriding the 'ids' parameter
                query_dict[key] = value

        print(query_dict)
        # Generate the URL for the report with applied filters and IDs
        generate_report_url = f"{reverse('admin:order_generate_report')}?{query_dict.urlencode()}"
        generate_bulk_order_report_url = f"{reverse('admin:download_bulk_orders_receipt')}?{query_dict.urlencode()}"
        
        extra_context["generate_report_url"] = generate_report_url
        extra_context["generate_bulk_order_report_url"] = generate_bulk_order_report_url
        


        return super().changelist_view(request, extra_context)
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "generate_reporting/",
                self.admin_site.admin_view(self.generate_report),
                name="order_generate_report",
            ),
            path(
                "<int:pk>/download_receipt/",
                self.admin_site.admin_view(self.download_receipt),
                name="order_download_receipt",
            ),
            path(
                "download_bulk_orders_receipt/",
                self.admin_site.admin_view(self.generate_bulk_receipts),
                name="download_bulk_orders_receipt",
            ),
        ]
        return custom_urls + urls
    def download_receipt(self, request, pk):
        """
        Generate and serve a receipt as an image for the given order.
        """
        try:
            # Get the order or raise Http404 if not found
            order = get_object_or_404(Order, pk=pk)

            # Fetch the associated order items
            order_items = order.items.all()

            # Generate HTML content for the receipt
            html_content = f"""
                <html>
                <head>
                    <title>Receipt for Order #{order.order_number}</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            margin: 20px;
                            padding: 10px;
                            border: 1px solid #ddd;
                            max-width: 600px;
                            margin: 0 auto;
                        }}
                        h1 {{
                            text-align: center;
                            font-size: 24px;
                            margin-bottom: 10px;
                        }}
                        .order-details {{
                            margin-bottom: 20px;
                        }}
                        .order-details p {{
                            font-size: 16px;
                            margin: 5px 0;
                        }}
                        .items {{
                            margin-top: 20px;
                        }}
                        .items table {{
                            width: 100%;
                            border-collapse: collapse;
                        }}
                        .items th, .items td {{
                            padding: 8px;
                            text-align: left;
                            border-bottom: 1px solid #ddd;
                        }}
                        .total {{
                            font-size: 18px;
                            margin-top: 20px;
                            text-align: right;
                        }}
                    </style>
                </head>
                <body>
                    <h1>Order Ticket</h1>

                    <div class="order-details">
                        <p><strong>Order Number:</strong> {order.order_number}</p>
                        <p><strong>Client Name:</strong> {order.client.name}</p>
                        <p><strong>Address:</strong> {order.client.delivery_address}</p>
                        <p><strong>Order Date:</strong> {order.order_date.strftime('%b %d, %Y')}</p>
                    </div>

                    <div class="items">
                        <h3>Order Items</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>Item</th>
                                    <th>Price</th>
                                    <th>Quantity</th>
                                    <th>Total</th>
                                </tr>
                            </thead>
                            <tbody>
            """

            # Add order items to the table
            for item in order_items:
                html_content += f"""
                    <tr>
                        <td>{item.subcategory}</td>
                        <td>${item.price:.2f}</td>
                        <td>{item.quantity}</td>
                        <td>${item.order_item_total_price:.2f}</td>
                    </tr>
                """

            # Add total price
            html_content += f"""
                </tbody>
            </table>
            <div class="total">
                <p><strong>Total: ${order.order_total_price:.2f}</strong></p>
            </div>
            </div>
            </body>
            </html>
            """

            # Define the output directory and file path
            output_dir = os.path.join(settings.MEDIA_ROOT, "generated_receipts")
            output_path = os.path.join(output_dir, f"{order.order_number}.png")

            # Ensure the directory exists, create if it doesn't
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Set the path for wkhtmltoimage executable if it's not in PATH
            path_to_wkhtmltoimage = "/usr/bin/wkhtmltoimage"  # Update this path if needed

            # Configure imgkit to use the wkhtmltoimage executable
            config = imgkit.config(wkhtmltoimage=path_to_wkhtmltoimage)

            # Generate the image from HTML content
            imgkit.from_string(html_content, output_path, config=config)

            # Serve the generated image as a file download
            try:
                return FileResponse(open(output_path, "rb"), as_attachment=True, filename=f"{order.order_number}.png")
            except FileNotFoundError:
                raise Http404(f"Receipt not found for order {order.order_number}.")
        except ImproperlyConfigured as e:
            # Return a 500 error in case of server configuration issues
            return HttpResponse(f"Error: {e}", status=500)
        except Http404 as e:
            # Handle 404 errors if the order or the file is not found
            return HttpResponse(f"Error: {e}", status=404)
        except Exception as e:
            # Catch any unexpected errors
            return HttpResponse(f"Unexpected error: {e}", status=500)
        
    def generate_bulk_receipts(self, request):
        """
        Generate and send receipt images for multiple orders as a ZIP archive without storing them on the server.
        """
        try:
            # os.environ['XDG_RUNTIME_DIR'] = '/tmp'
            os.environ['TMPDIR'] = '/var/tmp' 
            os.environ['XDG_RUNTIME_DIR'] = '/var/tmp'
            # Start with the filtered queryset based on current admin filters
            queryset = self.get_queryset(request)

            # Further filter the queryset if specific IDs are provided
            selected_ids = request.GET.getlist("ids")
            if selected_ids:
                queryset = queryset.filter(id__in=selected_ids)

            # Apply additional filters from the request
            filter_params = {key: value for key, value in request.GET.items() if key != "ids"}
            if filter_params:
                queryset = queryset.filter(**filter_params)

            # Check if any orders match the filter
            if not queryset.exists():
                return HttpResponse("No orders found to generate receipts.", status=400)

            # Create an in-memory buffer for the ZIP file
            zip_buffer = io.BytesIO()

            # Create a ZIP file in memory
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:

                # Generate receipts for each order
                for order in queryset:
                    # Fetch the associated order items
                    order_items = order.items.all()

                    # Generate HTML content for the receipt
                    html_content = f"""
                        <html>
                        <head>
                            <title>Receipt for Order #{order.order_number}</title>
                            <style>
                                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                                .header {{ text-align: center; font-size: 20px; margin-bottom: 20px; }}
                                .order-details {{ margin-bottom: 10px; }}
                                .order-details p {{ margin: 5px 0; }}
                                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                                th {{ background-color: #f2f2f2; }}
                                .total {{ text-align: right; font-weight: bold; margin-top: 10px; }}
                            </style>
                        </head>
                        <body>
                            <div class="header">Receipt for Order #{order.order_number}</div>
                            <div class="order-details">
                                <p><strong>Client:</strong> {order.client.name}</p>
                                <p><strong>Address:</strong> {order.client.delivery_address}</p>
                                <p><strong>Order Date:</strong> {order.order_date.strftime('%b %d, %Y')}</p>
                            </div>
                            <table>
                                <tr>
                                    <th>Item</th>
                                    <th>Price</th>
                                    <th>Quantity</th>
                                    <th>Total</th>
                                </tr>
                    """
                    for item in order_items:
                        html_content += f"""
                            <tr>
                                <td>{item.subcategory}</td>
                                <td>${item.price:.2f}</td>
                                <td>{item.quantity}</td>
                                <td>${item.order_item_total_price:.2f}</td>
                            </tr>
                        """
                    html_content += f"""
                            </table>
                            <div class="total">
                                Total: ${order.order_total_price:.2f}
                            </div>
                        </body>
                        </html>
                    """

                    # Create a temporary file to store the receipt image
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        # Configure imgkit to use wkhtmltoimage executable
                        config = imgkit.config(wkhtmltoimage="/usr/bin/wkhtmltoimage")  # Update the path as needed
                        imgkit.from_string(html_content, temp_file.name, config=config)

                        # Read the generated image from the temporary file
                        with open(temp_file.name, 'rb') as f:
                            receipt_image_data = f.read()

                        # Add the generated receipt to the ZIP file in memory
                        zip_file.writestr(f"receipt_{order.order_number}.png", receipt_image_data)

            # Seek to the beginning of the ZIP buffer
            zip_buffer.seek(0)

            # Prepare the response as a downloadable ZIP file
            response = HttpResponse(zip_buffer.read(), content_type="application/zip")
            response['Content-Disposition'] = 'attachment; filename="bulk_receipts.zip"'

            return response

        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}", status=500)
    def change_view(self, request, object_id, form_url="", extra_context=None):
        """
        Override the change view to add the download receipt URL to the context.
        """
        extra_context = extra_context or {}
        # Add the download receipt URL to the context with the correct `pk`
        extra_context["download_receipt_url"] = reverse(
            "admin:order_download_receipt", kwargs={"pk": object_id}
        )
        return super().change_view(request, object_id, form_url, extra_context)


class OrderItemAdmin(admin.ModelAdmin):
    """
    Admin panel for managing Order Items with a dynamically filtered total quantity displayed.
    """

    list_display = (
        "order",
        "category",
        "subcategory",
        "quantity",
        "price",
        "order_item_total_price",
        "deleted",
    )
    list_filter = (
         "order__status",
        ('category', RelatedOnlyFieldListFilter),
        ('subcategory', RelatedOnlyFieldListFilter),
        
    )
    search_fields = (
        "order__order_number",
        "category__name",
        "subcategory__name",
    )
    readonly_fields = (
        "order",
        "category",
        "subcategory",
        "quantity",
        "price",
        "order_item_total_price",
        "deleted",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
    autocomplete_fields = ("order", "category", "subcategory")
    list_display_links = None
    class Media:
        js = ("admin/js/total_quantity.js",)

    # Override change_form_template to remove save buttons
    change_list_template = "admin/orders/OrderItem/change_list.html"
    
    change_form_template = "admin/orders/OrderItem/order_item_no_save_buttons.html"

    def has_add_permission(self, request):
        return False

    # def has_delete_permission(self, request, obj=None):
        # return False
    
    def has_change_permission(self, request, obj=None):
        # If you want to prevent saving or modifying, return False
        return False

    def get_readonly_fields(self, request, obj=None):
        # Allow read-only fields as per your requirement
        return self.readonly_fields
    
    def generate_kitchen_report(self, request):
        """
        Generate a kitchen report summarizing total quantities of Order Items grouped by subcategory.
        """
        try:
            # Start with the filtered queryset based on current admin filters
            queryset = self.get_queryset(request)
    
            # Further filter the queryset if specific IDs are provided
            selected_ids = request.GET.getlist("ids")
            if selected_ids:
                queryset = queryset.filter(id__in=selected_ids)
    
            # if "order__status" not in filter_params or filter_params.get("order__status") != "Pending":
                # return HttpResponse("Please select the status as 'Pending' before generating the report.", status=400)
            
            filter_params = {key: value for key, value in request.GET.items() if key != "ids"}
            # Apply additional filters from the request (e.g., status__exact)
            if filter_params:
                queryset = queryset.filter(**filter_params)
    
            if not queryset.exists():
                return HttpResponse("No Data Found to Generate Report", status=400)
    
            # Summarize Total Quantities by Subcategory
            item_summary = {}
            for item in queryset:
                subcategory_name = item.subcategory.name if item.subcategory else "Uncategorized"
                if subcategory_name not in item_summary:
                    item_summary[subcategory_name] = 0
                item_summary[subcategory_name] += item.quantity
    
            # Generate PDF content
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
    
            # Add Title
            title = Paragraph("<strong>Kitchen Report</strong>", styles["Title"])
            elements.append(title)
            elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%b %d, %Y %H:%M:%S')}", styles["Normal"]))
            elements.append(Paragraph("<br/><br/>", styles["Normal"]))
    
            # Add Item Summary Table
            summary_data = [["Subcategory", "Total Quantity"]]
            for subcategory, total_quantity in sorted(item_summary.items()):
                summary_data.append([subcategory, total_quantity])
    
            summary_table = Table(summary_data, colWidths=[250, 100])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ]))
            elements.append(summary_table)
    
            # Build PDF
            doc.build(elements)
            pdf_buffer.seek(0)
    
            # Return the PDF as a file download
            response = HttpResponse(pdf_buffer, content_type="application/pdf")
            response["Content-Disposition"] = "attachment; filename=kitchen_report.pdf"
            return response
    
        except Exception as e:
            return HttpResponse(f"An error occurred while generating the kitchen report: {e}", status=500)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "generate_kitchen_report/",
                self.admin_site.admin_view(self.generate_kitchen_report),
                name="order_generate_kitchen_report",
            ),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        # Get the filtered queryset
        queryset = self.get_queryset(request)

        # Serialize the IDs of the filtered queryset
        filtered_ids = list(queryset.values_list("id", flat=True))
        query_dict = QueryDict(mutable=True)
        query_dict.setlist("ids", filtered_ids)

        # Include filters from the current request
        for key, value in request.GET.items():
            if key != "ids":
                query_dict[key] = value

        # Generate URLs for both reports
        extra_context["generate_kitchen_report_url"] = f"{reverse('admin:order_generate_kitchen_report')}?{query_dict.urlencode()}"

        return super().changelist_view(request, extra_context)


    
class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0  # This hides the 'Add another attachment' button
    fields = ("file",)  # Display only the file field

    def get_readonly_fields(self, request, obj=None):
        """
        Make the file field read-only if the attachment already exists.
        """
        if obj and obj.pk:
            return ("file",)  # Make the file read-only for existing attachments
        return self.readonly_fields  # Otherwise, allow adding new files

    # Remove the 'DELETE?' checkbox and 'Add another Attachment' option
    def has_add_permission(self, request, obj=None):
        return False  # Disable the ability to add new attachments

    # def has_delete_permission(self, request, obj=None):
        # return False  # Disable the ability to delete attachments


class SupportTicketAdmin(admin.ModelAdmin):
    # Display the most relevant columns in the list view
    list_display = (
        "ticket_id",
        "title",
        "user",
        "priority",
        "category",
        "status",
        "created_at",
        "updated_at",
    )

    # Add filters for easy navigation of tickets
    list_filter = ("priority", "status", "category","created_at" ,("user",RelatedOnlyFieldListFilter))

    # Enable search for ticket ID, title, and user
    search_fields = ("ticket_id", "title", "user__username")

    # Allow admin to filter tickets by category, status, and priority
    list_editable = ("status",)  # Allow editing the status directly from the list view

    # Custom ordering to display the most recent tickets first
    ordering = ("-created_at",)

    # Exclude the 'created_at' and 'updated_at' fields from the form
    exclude = ("created_at", "updated_at")

    # Add helpful fieldsets and labels for better user understanding
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "status",
                    "ticket_id",
                    "title",
                    "user",
                    "priority",
                    "category",
                )
            },
        ),
        ("Details", {"fields": ("description",), "classes": ("collapse",)}),
    )

    # Make all fields read-only except 'status'
    readonly_fields = (
        "ticket_id",
        "title",
        "user",
        "priority",
        "category",
        "description",
        "created_at",
        "updated_at",
    )

    # Add the inline Attachment model to the SupportTicket admin
    inlines = [AttachmentInline]

    def get_readonly_fields(self, request, obj=None):
        """
        Make all fields read-only except for 'status' if editing an existing ticket.
        """
        # Only make 'status' editable when modifying an existing SupportTicket
        if obj:
            return (
                self.readonly_fields
            )  # For existing tickets, keep status editable and others read-only
        return (
            self.readonly_fields
        )  # For creating new objects, all fields are read-only

    def has_add_permission(self, request):
        """Disable add functionality for Orders."""
        return False
    


# # Customize the UserAdmin to display clients and their orders
# class CustomUserAdmin(UserAdmin):
#     def get_queryset(self, request):
#         queryset = super().get_queryset(request)
#         return queryset.filter(is_superuser=False)  # Exclude superusers

#     # Custom method to generate a clickable link to the client's admin page
#     def get_clients_link(self, obj):
#         # Assuming that the 'Client' model has a foreign key to 'User' (Agency)
#         # 'obj' here represents the User instance
#         clients = obj.client_name.all()  # Get all clients related to the user
#         if clients:
#             # Create a link to the client's admin page
#             client_links = []
#             for client in clients:
#                 # Generate the URL for each client admin page
#                 client_url = f"/admin/user/client/{client.id}/change/"
#                 client_links.append(f'<a href="{client_url}">{client.name}</a>')
#             return format_html(", ".join(client_links))
#         return "No Clients"

#     get_clients_link.short_description = "Clients"  # Set the column title in the admin list

#     list_display = [
#         "email",
#         "username",
#         "is_active",
#         "email_verified",
#         "profile_picture",
#         "get_clients_link",  # Display the clients' links in the User Admin page
#     ]

#     search_fields = ["email", "username"]
#     list_filter = ["is_active", "email_verified"]

#     readonly_fields = (
#         "email",
#         "username",
#         "profile_picture",
#         "is_active",
#         "email_verified",
#         "otp",
#         "is_staff",
#         "is_superuser",
#         "deleted",
#     )

#     fieldsets = (
#         (None, {"fields": ("email", "username", "profile_picture", "is_active", "email_verified", "otp")}),
#     )

#     add_fieldsets = (
#         (None, {
#             "classes": ("wide",),
#             "fields": ("email", "username", "password1", "password2", "is_active", "email_verified"),
#         }),
#     )

#     exclude = ("groups", "user_permissions", "deleted")

#     inlines = [ClientInline]  # Add the ClientInline to show clients under the User (Agency)

    # def has_delete_permission(self, request, obj=None):
        # """Disable delete functionality for Orders."""
        # return False


# Register the User model with the custom UserAdmin
# Register the User model with the custom UserAdmin
# Register the custom admin views
# Unregister default models
# admin.site.unregister(OutstandingToken)
# admin.site.unregister(BlacklistedToken)
# admin.site.unregister(Group)
# admin.site.unregister(OutstandingToken)
# admin.site.unregister(BlacklistedToken)
class OrderInline(admin.TabularInline):
    model = Order
    extra = 0  # No extra empty forms by default
    fields = ("order_number_link", "order_date", "status", "order_total_price")
    readonly_fields = ("order_number_link", "order_date", "status", "order_total_price")  # Make the custom field readonly

    def has_add_permission(self, request, obj=None):
        return False  # Prevent adding new orders from the client admin page

    def has_delete_permission(self, request, obj=None):
        return False  # Prevent deleting orders from the client admin page

    def has_change_permission(self, request, obj=None):
        return False  # Prevent changing orders from the client admin page

    # Custom method to generate a clickable link for order_number
    def order_number_link(self, obj):
        order_url = f"/admin/orders/order/{obj.id}/change/"  # Assuming 'user' is your app name
        return format_html('<a href="{}">{}</a>', order_url, obj.order_number)

    order_number_link.short_description = "Order Number"
# Customizing the Client Admin Panel

class AgencyFilter(SimpleListFilter):
    title = _("Agency Name")  # Changed the title to "Agency Name"
    parameter_name = "user"

    def lookups(self, request, model_admin):
        # Display only users associated with agencies
        return (
            (user.id, user.username)
            for user in User.objects.filter(client_name__isnull=False).distinct()
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user_id=self.value())
        return queryset

class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "delivery_address", "user", "order_count")
    search_fields = ("name", "user__username")
    list_filter = (AgencyFilter,)  # This is the updated filter
    inlines = [OrderInline]
    readonly_fields = (
        "name",
        "delivery_address",
        "user",
        "order_count",
    )

    def order_count(self, obj):
        return obj.order_client.count()

    order_count.short_description = _("Number of Orders")

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset

    def get_model_perms(self, request):
        perms = super().get_model_perms(request)
        perms["change"] = True
        return perms


# Unregister Blacklisted and Outstanding tokens
if admin.site.is_registered(BlacklistedToken):
    admin.site.unregister(BlacklistedToken)

if admin.site.is_registered(OutstandingToken):
    admin.site.unregister(OutstandingToken)
# Register your custom models

admin.site.register(Category, CategoryAdmin)
admin.site.register(Client, ClientAdmin)

admin.site.register(SubCategory, SubCategoryAdmin)


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)

admin.site.register(Support_ticket, SupportTicketAdmin)
# admin.site.register(User, CustomUserAdmin)
