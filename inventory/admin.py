from django.contrib import admin
from defaults.admin import DefaultAdmin

from .models import *
from .helpers import copy_product

def copy_product_action(modeladmin, request, queryset):
    for obj in queryset:
        copy_product(obj)
copy_product_action.short_description = "Copy Product"


class MaterialAdmin(DefaultAdmin):
    list_display = ['name', 'quantity_in_stock', 'sku_supplier', 'supplier']
    list_filter = ['supplier', 'mat_type']
    search_fields = ['name', 'supplier__business_name']

class ProductPatternInline(admin.TabularInline):
    model=ProductPattern
    extra = 0

class ProductModelImageInline(admin.TabularInline):
    model=ProductModelImage
    extra=0

class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['number', 'size', 'all_patterns_present', 'product_images_present']
    inlines = [ProductPatternInline, ProductModelImageInline]
    readonly_fields = ['used_in_collections']

class BillOfMaterialInline(admin.TabularInline):
    model = BillOfMaterial
    readonly_fields = ['all_materials_in_stock',]
    extra = 0

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0

class ProductAdmin(DefaultAdmin):
    readonly_fields = (
        'sku',
        'recommended_retail_price', 
        'recommended_B2B_price_per_1',
        'recommended_B2B_price_per_6',
        'recommended_B2B_price_per_24',
        'recommended_B2B_price_per_96',
        'cost',
        )    
    list_display = ['name','sku', 'active', 'complete', 'all_materials_in_stock']        
    list_filter = ['collection', 'colour', 'model__size', 'model__number', 'complete', 'active']
    inlines = [BillOfMaterialInline, ProductImageInline]
    actions = [copy_product_action]

class BillOfMaterialAdmin(admin.ModelAdmin):
    readonly_fields = ['all_materials_in_stock']

admin.site.register(Material, MaterialAdmin)
admin.site.register(Collection)
admin.site.register(Size)
admin.site.register(Colour)
admin.site.register(ProductPattern)
admin.site.register(ProductModel, ProductModelAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(BillOfMaterial, BillOfMaterialAdmin)