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

from django.core.exceptions import ImproperlyConfigured
from html2image import Html2Image

class CustomAdminSite(AdminSite):
    site_header = (
        "AgelessEatsKitchen.com Admin"  # Custom header text for the admin panel
    )
    site_title = "AgelessEatsKitchen Admin"  # Title text in the browser tab
    index_title = "Welcome to AgelessEatsKitchen Admin"  # Title for the index page in the admin panel


from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from html2image import Html2Image
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
    list_filter = ("category",)  # Filters for deletion and category
    ordering = ("category", "name")  # Default ordering
    autocomplete_fields = ("category",)  # Autocomplete for category selection

    # Add a dropdown filter for related subcategories
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("category")  # Optimize queries with related fields


class OrderItemInline(admin.TabularInline):
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

    inlines = [OrderItemInline]
    list_display = (
        "order_number",
        "user",
        "status",
        "get_client_name",
        "order_total_price",
        "order_date",
    )
    list_filter = ("status", "order_date", "deleted", "user")
    search_fields = (
        "order_number",
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

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        """
        Override the `get_urls` method to add custom URLs.
        """
        urls = super().get_urls()
        custom_urls = [
            # Custom URL pattern for downloading receipts
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

            # Generate HTML content for the receipt
            html_content = f"""
                <html>
                <head><title>Receipt</title></head>
                <body>
                    <h1>Receipt for Order {order.order_number}</h1>
                    <p>Client Name: {order.client.name}</p>
                    <p>Total Price: ₹{order.order_total_price}</p>
                    <p>Order Date: {order.order_date}</p>
                </body>
                </html>
            """

            # Define the output directory and file path
            output_dir = os.path.join(settings.MEDIA_ROOT, "generated_receipts")
            output_path = os.path.join(output_dir, f"{order.order_number}.png")

            # Ensure the directory exists, create if it doesn't
            try:
                os.makedirs(output_dir, exist_ok=True)
            except OSError as e:
                raise ImproperlyConfigured(f"Failed to create directory {output_dir}: {e}")

            try:
                # Set custom browser path if needed
                os.environ["CHROME_PATH"] = "/usr/bin/chromium-browser"
                hti = Html2Image(browser_executable="/usr/bin/chromium-browser", output_path=output_dir)
                hti.screenshot(html_str=html_content, save_as=f"{order.order_number}.png")
            except Exception as e:
                raise ImproperlyConfigured(f"Error generating receipt for order {order.order_number}: {e}")

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

    def has_delete_permission(self, request, obj=None):
        return False
    
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

    def has_delete_permission(self, request, obj=None):
        return False  # Disable the ability to delete attachments


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


class CustomUserAdmin(UserAdmin):
    # Override the get_queryset method to exclude superusers
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_superuser=False)  # Exclude superusers

    # Optionally, you can customize the list display fields if needed
    list_display = [
        "email",
        "username",
        "is_active",
        "email_verified",
        "profile_picture",
    ]
    search_fields = ["email", "username"]
    list_filter = ["is_active", "email_verified"]

    # Remove the Groups and Permissions sections in the admin form
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "username",
                    "profile_picture",
                    "is_active",
                    "email_verified",
                    "otp",
                )
            },
        ),
        ("Permissions", {"fields": ("is_staff", "is_superuser", "deleted")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "is_active",
                    "email_verified",
                ),
            },
        ),
    )

    # You can remove the "groups" and "user_permissions" fields from the form
    exclude = ("groups", "user_permissions", "Deleted")

    def has_delete_permission(self, request, obj=None):
        """Disable delete functionality for Orders."""
        return False


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
    fields = ("order_number", "order_date", "status", "order_total_price")
    readonly_fields = ("order_number", "order_date", "status", "order_total_price")

    def has_add_permission(self, request, obj=None):
        return False  # Prevent adding new orders from the client admin page

    def has_delete_permission(self, request, obj=None):
        return False  # Prevent deleting orders from the client admin page

    def has_change_permission(self, request, obj=None):
        return False  # Prevent changing orders from the client admin page


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

    def has_delete_permission(self, request, obj=None):
        return False  # Disable deleting clients


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
admin.site.register(User, CustomUserAdmin)
