from django.contrib import admin
from defaults.admin import DefaultAdmin

from .models import *
from .helpers import copy_product, copy_product_model

def copy_product_action(modeladmin, request, queryset):
    for obj in queryset:
        copy_product(obj)
copy_product_action.short_description = "Copy Product"

def copy_product_model_action(modeladmin, request, queryset):
    for obj in queryset:
        copy_product_model(obj)
copy_product_model_action.short_description = "Copy product-model without patterns"

class StockLocationItemInline(admin.TabularInline):
    model=StockLocationItem
    extra=0

class StockLocationAdmin(admin.ModelAdmin):
    inlines = [StockLocationItemInline]

class MaterialAdmin(DefaultAdmin):
    list_display = ['name', 'sku_supplier', 'supplier']
    list_filter = ['supplier', 'mat_type']
    search_fields = ['name', 'supplier__business_name']
    inlines = [StockLocationItemInline]

class ProductPatternInline(admin.TabularInline):
    model=ProductPattern
    extra = 0

class ProductModelImageInline(admin.TabularInline):
    model=ProductModelImage
    extra=0

class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'product_type', 'number', 'size', 'all_patterns_present', 'product_images_present']
    list_filter = ['product_type', 'number', 'size', 'all_patterns_present', 'product_images_present']
    inlines = [ProductPatternInline, ProductModelImageInline]
    readonly_fields = ['used_in_collections']
    actions = [copy_product_model_action]

class BillOfMaterialInline(admin.TabularInline):
    model = BillOfMaterial
    readonly_fields = [] #['materials_on_stock',]
    extra = 0

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0

class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('sku', 'recommended_retail_price', 'recommended_B2B_price_per_1',
        'recommended_B2B_price_per_6', 'recommended_B2B_price_per_24',
        'recommended_B2B_price_per_96', 'cost', 'materials_on_stock',)    
    list_display = ['name','sku', 'active', 'complete', 'materials_on_stock',
        'recommended_retail_price', 'recommended_B2B_price_per_1',
        'recommended_B2B_price_per_6', 'recommended_B2B_price_per_24', 
        'recommended_B2B_price_per_96']  
    list_filter = ['collection', 'colour', 'model__product_type', 'model__size', 'model__number', 'complete', 'active']
    inlines = [BillOfMaterialInline, ProductImageInline]
    actions = [copy_product_action]


class BillOfMaterialAdmin(admin.ModelAdmin):
    readonly_fields = []

admin.site.register(StockLocation, StockLocationAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(StockLocationItem)
admin.site.register(Collection)
admin.site.register(Size)
admin.site.register(Colour)
admin.site.register(ProductPattern)
admin.site.register(ProductModel, ProductModelAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(BillOfMaterial, BillOfMaterialAdmin)