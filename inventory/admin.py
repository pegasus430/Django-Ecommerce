from django.contrib import admin

from models import *

class ProductPatternInline(admin.TabularInline):
    model=ProductPattern
    extra = 1

class ProductModelImageInline(admin.TabularInline):
    model=ProductModelImage
    extra=1

class ProductModelAdmin(admin.ModelAdmin):
    inlines = [ProductPatternInline, ProductModelImageInline]

class BillOfMaterialInline(admin.StackedInline):
    model = BillOfMaterial
    extra = 2

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('cost', 'recommended_shop_price', 'recommended_retail_price', 'sku')
    inlines = [BillOfMaterialInline, ProductImageInline]

admin.site.register(Supplier)
admin.site.register(Material)
admin.site.register(Collection)
admin.site.register(Size)
admin.site.register(ProductPattern)
admin.site.register(ProductModel, ProductModelAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(BillOfMaterial)