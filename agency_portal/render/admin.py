from django.contrib import admin
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from menukit.models import Category, SubCategory
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from user.models import User
from orders.models import Order,OrderItem
from support_ticket.models import Support_ticket,Attachment
from django.contrib.auth.models import Group

from django.contrib import admin
from django.contrib.admin import AdminSite
from rest_framework_simplejwt.token_blacklist import models

# Unregister Blacklisted and Outstanding tokens

class CustomAdminSite(AdminSite):
    site_header = "AgelessEatsKitchen.com Admin"  # Custom header text for the admin panel
    site_title = "AgelessEatsKitchen Admin"  # Title text in the browser tab
    index_title = "Welcome to AgelessEatsKitchen Admin"  # Title for the index page in the admin panel

# Register the custom admin site
admin.site = CustomAdminSite()

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'deleted')  # Display columns
    search_fields = ('name',)  # Search bar
    list_filter = ('deleted',)  # Filter by 'deleted' field
    ordering = ('name',)  # Default ordering


class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'deleted')  # Display columns
    search_fields = ('name', 'category__name')  # Search bar with category name support
    list_filter = ('category',)  # Filters for deletion and category
    ordering = ('category', 'name')  # Default ordering
    autocomplete_fields = ('category',)  # Autocomplete for category selection

    # Add a dropdown filter for related subcategories
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category')  # Optimize queries with related fields

class OrderItemInline(admin.TabularInline):
    """
    Inline admin to display OrderItem details within the Order panel.
    """
    model = OrderItem
    extra = 0  # No extra empty forms by default
    fields = ('category', 'subcategory', 'quantity', 'price', 'order_item_total_price')
    readonly_fields = ('order_item_total_price',)  # Make 'order_item_total_price' read-only
    autocomplete_fields = ('category', 'subcategory')  # Autocomplete for related fields

    def get_readonly_fields(self, request, obj=None):
        """
        Ensure all fields in OrderItem are read-only in the inline.
        """
        readonly_fields = ['category', 'subcategory', 'quantity', 'price', 'order_item_total_price']
        if obj:  # If obj exists, it's an existing OrderItem, make the fields read-only
            return readonly_fields
        return readonly_fields # Autocomplete for related fields
    
    def has_add_permission(self, request, obj=None):
        return False  # Disable the ability to add new attachments

    def has_delete_permission(self, request, obj=None):
        return False  # Disable the ability to delete attachments

    
class OrderAdmin(admin.ModelAdmin):
    """
    Admin panel for managing Orders, with only the 'status' field editable.
    """
    list_display = ('order_number', 'user', 'status','customer_name', 'order_total_price', 'order_date')
    list_filter = ('status', 'order_date', 'deleted', 'user')  # Filters for status, date, and user
    search_fields = ('order_number', 'user__username', 'customer_name', 'delivery_address')  # Search bar fields
    ordering = ('-order_date',)
    list_editable = ('status',)# Default ordering by newest orders
    date_hierarchy = 'order_date'  # Date hierarchy navigation
    inlines = [OrderItemInline]  # Inline display for OrderItems

    def get_readonly_fields(self, request, obj=None):
        """
        Make all fields read-only except for the 'status' field if editing an existing Order.
        """
        # List of fields to be read-only for both new and existing orders
        readonly_fields = [
            'user', 'customer_name', 'order_number', 'order_date', 'special_instructions',
            'delivery_address', 'order_total_price', 'deleted', 'created_at', 'updated_at'
        ]
        
        # If obj is not None (i.e., an existing order), add 'status' as editable
        if obj:
            return readonly_fields  # Do not add 'status' here, so it remains editable
        return readonly_fields  # For new orders, keep everything read-only

    def has_add_permission(self, request):
        """Disable add functionality for Orders."""
        return False

    def has_change_permission(self, request, obj=None):
        """Allow view access but disable editing except for the 'status' field."""
        return True  # We allow viewing but will restrict editing in get_readonly_fields

    def has_delete_permission(self, request, obj=None):
        """Disable delete functionality for Orders."""
        return True
    
class OrderItemAdmin(admin.ModelAdmin):
    """
    Admin panel for managing individual Order Items, with all fields read-only.
    """
    list_display = ('order', 'category', 'subcategory', 'quantity', 'price', 'order_item_total_price', 'deleted')
    list_filter = ('order__status', 'category', 'subcategory', 'deleted')  # Filters for order status, category, etc.
    search_fields = ('order__order_number', 'category__name', 'subcategory__name')  # Search bar fields
    readonly_fields = (
        'order', 'category', 'subcategory', 'quantity', 'price', 'order_item_total_price', 'deleted', 'created_at', 'updated_at'
    )  # Make all fields read-only
    ordering = ('-created_at',)  # Default ordering by newest items
    autocomplete_fields = ('order', 'category', 'subcategory') 
    
    
    
class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0  # This hides the 'Add another attachment' button
    fields = ('file',)  # Display only the file field

    def get_readonly_fields(self, request, obj=None):
        """
        Make the file field read-only if the attachment already exists.
        """
        if obj and obj.pk:
            return ('file',)  # Make the file read-only for existing attachments
        return self.readonly_fields  # Otherwise, allow adding new files

    # Remove the 'DELETE?' checkbox and 'Add another Attachment' option
    def has_add_permission(self, request, obj=None):
        return False  # Disable the ability to add new attachments

    def has_delete_permission(self, request, obj=None):
        return False  # Disable the ability to delete attachments



class SupportTicketAdmin(admin.ModelAdmin):
    # Display the most relevant columns in the list view
    list_display = ('ticket_id', 'title', 'user', 'priority', 'category', 'status', 'created_at', 'updated_at')
    
    # Add filters for easy navigation of tickets
    list_filter = ('priority', 'status', 'category', 'created_at','user')
    
    # Enable search for ticket ID, title, and user
    search_fields = ('ticket_id', 'title', 'user__username')
    
    # Allow admin to filter tickets by category, status, and priority
    list_editable = ('status',)  # Allow editing the status directly from the list view
    
    # Custom ordering to display the most recent tickets first
    ordering = ('-created_at',)
    
    # Exclude the 'created_at' and 'updated_at' fields from the form
    exclude = ('created_at', 'updated_at')

    # Add helpful fieldsets and labels for better user understanding
    fieldsets = (
        (None, {
            'fields': ('status','ticket_id', 'title', 'user', 'priority', 'category')
        }),
        ('Details', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )

    # Make all fields read-only except 'status'
    readonly_fields = ('ticket_id', 'title', 'user', 'priority', 'category', 'description', 'created_at', 'updated_at')

    # Add the inline Attachment model to the SupportTicket admin
    inlines = [AttachmentInline]

    def get_readonly_fields(self, request, obj=None):
        """
        Make all fields read-only except for 'status' if editing an existing ticket.
        """
        # Only make 'status' editable when modifying an existing SupportTicket
        if obj:
            return self.readonly_fields  # For existing tickets, keep status editable and others read-only
        return self.readonly_fields  # For creating new objects, all fields are read-only

    def has_add_permission(self, request):
        """Disable add functionality for Orders."""
        return False



class CustomUserAdmin(UserAdmin):
    # Override the get_queryset method to exclude superusers
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(is_superuser=False)  # Exclude superusers

    # Optionally, you can customize the list display fields if needed
    list_display = ['email', 'username', 'is_active', 'email_verified', 'profile_picture']
    search_fields = ['email', 'username']
    list_filter = ['is_active', 'email_verified']

    # Remove the Groups and Permissions sections in the admin form
    fieldsets = (
        (None, {'fields': ('email', 'username', 'profile_picture', 'is_active', 'email_verified', 'otp')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'deleted')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_active', 'email_verified'),
        }),
    )

    # You can remove the "groups" and "user_permissions" fields from the form
    exclude = ('groups', 'user_permissions','Deleted')
    
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

# Unregister Blacklisted and Outstanding tokens
if admin.site.is_registered(BlacklistedToken):
    admin.site.unregister(BlacklistedToken)

if admin.site.is_registered(OutstandingToken):
    admin.site.unregister(OutstandingToken)
# Register your custom models

admin.site.register(Category,CategoryAdmin)
admin.site.register(SubCategory,SubCategoryAdmin)



admin.site.register(Order,OrderAdmin)
admin.site.register(Support_ticket,SupportTicketAdmin)
admin.site.register(User,CustomUserAdmin)
