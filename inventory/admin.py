from django.contrib import admin

from models import *

class ProductPatternInline(admin.TabularInline):
    model=ProductPattern
    extra = 0

class ProductModelImageInline(admin.TabularInline):
    model=ProductModelImage
    extra=0

class ProductModelAdmin(admin.ModelAdmin):
    inlines = [ProductPatternInline, ProductModelImageInline]
    readonly_fields = ['used_in_collections']

class BillOfMaterialInline(admin.TabularInline):
    model = BillOfMaterial
    extra = 0

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0

class ProductAdmin(admin.ModelAdmin):
    readonly_fields = (
        'sku',
        'recommended_retail_price', 
        'recommended_B2B_price_per_1',
        'recommended_B2B_price_per_6',
        'recommended_B2B_price_per_24',
        'recommended_B2B_price_per_96',
        'cost',
        )        

    inlines = [BillOfMaterialInline, ProductImageInline]

admin.site.register(Material)
admin.site.register(Collection)
admin.site.register(Size)
admin.site.register(Colour)
admin.site.register(ProductPattern)
admin.site.register(ProductModel, ProductModelAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(BillOfMaterial)