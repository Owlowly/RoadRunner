from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Type, Category, Product, Size


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']


class SizeInline(admin.TabularInline):
    model = Product.size.through
    extra = 1


@admin.register(Type)
class TypeAdmin(TranslatableAdmin):
    list_display = ['name', 'slug']
    # prepopulated_fields = {'slug': ('name', )}

    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ['name', 'slug']
    # prepopulated_fields = {'slug': ('name', )}

    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_display = ['name', 'slug', 'price', 'available', 'created', 'updated', 'display_sizes']
    # prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('size',)
    # inlines = [SizeInline]

    def display_sizes(self, obj):
        return ', '.join([str(size.name) for size in obj.size.all()])
    display_sizes.short_description = 'Sizes'

    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}
