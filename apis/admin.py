from django.contrib import admin
from .models import *

# Admin class for User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'user_type', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('user_type', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('name', 'email', 'phone_number', 'user_type', 'verified')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

# Admin class for Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'price', 'quantity', 'remaining_quantity', 'unlist')
    list_filter = ('user', 'unlist')
    search_fields = ('name', 'user__username')
    ordering = ('name',)

# Admin class for ProductImage
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')
    search_fields = ('product__name',)

# Admin class for Contract
@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'consumer', 'product', 'quantity', 'accepted', 'completed', 'created_at')
    list_filter = ('accepted', 'completed', 'created_at')
    search_fields = ('farmer__username', 'consumer__username', 'product__name')

# Admin class for FarmerVerificationDocs
@admin.register(FarmerVerificationDocs)
class FarmerVerificationDocsAdmin(admin.ModelAdmin):
    list_display = ('user', 'addhar_card', 'pan_card', 'satbaarcopy')
    search_fields = ('user__username',)

# Admin class for ConsumerVerificationDocs
@admin.register(ConsumerVerificationDocs)
class ConsumerVerificationDocsAdmin(admin.ModelAdmin):
    list_display = ('user', 'addhar_card', 'pan_card')
    search_fields = ('user__username',)
