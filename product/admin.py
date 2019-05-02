from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['title']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'tag_final_value', 'qty', 'active']
    list_select_related = ['category']
    list_filter = ['active', 'category']
    search_fields = ['title']
    list_per_page = 50
    fields = ['active', 'title', 'category', 'qty', 'value', 'discount_value', 'tag_final_value']
    autocomplete_fields = ['category']
    readonly_fields = ['tag_final_value']
