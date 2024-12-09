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
from django.conf import settings
import os
import imgkit
from django.core.exceptions import ImproperlyConfigured
from django.http import QueryDict
from django.urls import reverse

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


class CategoryFilter(admin.SimpleListFilter):
    title = 'Menu'  # This will change the filter label to "Menu"
    parameter_name = 'category'  # This is still the category field you're filtering by
    
    def lookups(self, request, model_admin):
        return [(category.id, category.name) for category in Category.objects.all()]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category__id=self.value())
        return queryset

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "deleted")  # Display columns
    search_fields = ("name", "category__name")  # Search bar with category name support
    list_filter = (CategoryFilter,)  # Correct way to add the filter class
    ordering = ("category", "name")  # Default ordering
    autocomplete_fields = ("category",)  # Autocomplete for category selection

    def get_search_results(self, request, queryset, search_term):
        return queryset

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("category")
    
class OrderItemInline2(admin.TabularInline):
    """
    Inline admin to display OrderItem details within the Order panel.
    """

    model = OrderItem
    extra = 0
    fields = ("category", "subcategory", "quantity", "price", "order_item_total_price")
    readonly_fields = ("order_item_total_price",)
    autocomplete_fields = ("category", "subcategory")

    def get_readonly_fields(self, request, obj=None):
        """
        Ensure all fields in OrderItem are read-only in the inline.
        """
        return self.fields if obj else super().get_readonly_fields(request, obj)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderAdmin(admin.ModelAdmin):
    """
    Admin panel for managing Orders, with the 'status' field editable.
    """

    inlines = [OrderItemInline2]
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
    list_filter = ("status", "order_date", "deleted", "user")
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
        Generate a consolidated report of the filtered orders and their items as an image.
        """
        try:
            # Extract order IDs from the query parameters
            order_ids = request.GET.getlist("ids")
            if not order_ids:
                return HttpResponse("No orders selected for the report.", status=400)

            # Fetch the orders and prefetch related items
            orders = Order.objects.filter(id__in=order_ids).prefetch_related("items")

            # Generate HTML for the report
            html_content = """
                <html>
                <head>
                    <title>Order Report</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; }
                        h1 { text-align: center; font-size: 24px; margin-bottom: 20px; }
                        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                        th { background-color: #f4f4f4; }
                        td { vertical-align: top; }
                        .order-details { margin-bottom: 20px; }
                        .order-items { margin-top: 10px; }
                        .order-items div { margin-bottom: 5px; }
                    </style>
                </head>
                <body>
                    <h1>Order Report</h1>
            """

            # Populate the HTML content with order and item data
            for order in orders:
                # Start with the order details
                order_details = f"""
                    <div class="order-details">
                        <h2>Order Number: {order.order_number}</h2>
                        <p><strong>Client Name:</strong> {order.client.name if order.client else 'N/A'}</p>
                        <p><strong>Order Date:</strong> {order.order_date.strftime('%b %d, %Y')}</p>
                """

                # Now add the items for this particular order
                items_html = ""
                for item in order.items.all():
                    items_html += f"""
                        <div>
                            <strong>Item:</strong> {item.category} - 
                            <strong>Qty:</strong> {item.quantity} - 
                            <strong>Price:</strong> ${item.price:.2f} - 
                            <strong>Total:</strong> ${item.order_item_total_price:.2f}
                        </div>
                    """

                order_details += f"""
                    <div class="order-items">
                        <h3>Items:</h3>
                        {items_html}
                    </div>
                    </div>
                """
                html_content += order_details

            # Close the HTML tags
            html_content += """
                </body>
                </html>
            """

            # Define the output path for the report image
            output_dir = os.path.join(settings.MEDIA_ROOT, "order_reports")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "filtered_order_report.png")

            # Set the path for wkhtmltoimage executable
            path_to_wkhtmltoimage = "/usr/bin/wkhtmltoimage"
            config = imgkit.config(wkhtmltoimage=path_to_wkhtmltoimage)

            # Generate the image
            imgkit.from_string(html_content, output_path, config=config)

            # Serve the image as a file download
            return FileResponse(open(output_path, "rb"), as_attachment=True, filename="filtered_order_report.png")

        except Exception as e:
            return HttpResponse(f"An error occurred while generating the report: {e}", status=500)
    # @admin.action(description="Download Report of Selected Orders")
    # def generate_report_action(self, request, queryset):
        # return self.generate_report(request, queryset)
    
    def changelist_view(self, request, extra_context=None):
        """
        Add a custom button for generating a report in the changelist view.
        """
        extra_context = extra_context or {}

        # Get the filtered queryset based on changelist filters
        queryset = self.get_queryset(request)

        # Serialize the queryset's IDs into query parameters
        query_dict = QueryDict(mutable=True)
        query_dict.setlist("ids", queryset.values_list("id", flat=True))

        # Create the URL with the serialized query parameters
        generate_report_url = f"{reverse('admin:order_generate_report')}?{query_dict.urlencode()}"
        extra_context["generate_report_url"] = generate_report_url

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
        "category",
        "subcategory",
        "deleted",
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
    list_filter = ("priority", "status", "category", "created_at", "user")

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
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "delivery_address", "user", "order_count")
    search_fields = ("name", "user__username")
    list_filter = ("user",)
    inlines = [
        OrderInline
    ]  # Orders will be displayed inline within Client details page
    readonly_fields = (
        "name",
        "delivery_address",
        "user",
        "order_count",
    )  # Add all fields you want to be read-only

    # Display the number of orders linked to each client
    def order_count(self, obj):
        return obj.order_client.count()  # Counts the number of orders for each client

    order_count.short_description = "Number of Orders"

    def has_add_permission(self, request):
        return False  # Disable adding new clients

    # def has_delete_permission(self, request, obj=None):
        # return False  # Disable deleting clients


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
