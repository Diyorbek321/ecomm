from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from app.models import User, Product, Order, Category


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'is_seller', 'is_customer', 'date_joined')
    list_filter = ('is_seller', 'is_customer', 'date_joined')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('-date_joined',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    list_editable = ('price', 'stock')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_price', 'status')
    list_filter = ['status']
    search_fields = ('user__username', 'user__email')
    # ordering = ('-ordered_at',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
