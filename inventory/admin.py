from django.contrib import admin
from defaults.admin import DefaultAdmin, DefaultInline

from .models import *

###############
### Inlines ###
###############
class SizeBreedsInline(DefaultInline):
    model = SizeBreed

class MaterialImageInline(DefaultInline):
    model=MaterialImage

class MaterialDataSheetInline(DefaultInline):
    model=MaterialDataSheet

class StockLocationItemInline(DefaultInline):
    model=StockLocationItem

class ProductModelPatternInline(DefaultInline):
    model=ProductModelPattern

class UmbrellaProductModelImageInline(DefaultInline):
    model=UmbrellaProductModelImage

class UmbrellaProductModelProductionDescriptionInline(DefaultInline):
    model=UmbrellaProductModelProductionDescription

class ProductModelInline(DefaultInline):
    model=ProductModel

class UmbrellaProductInline(DefaultInline):
    model=UmbrellaProduct  
    extra=0
    fields = ('name', 'umbrella_product_model',)  
    exclude = ('description', 'complete', 'active')
    readonly_fields = ('colour',)
    can_delete = False

class UmbrellaProductBillOfMaterialInline(admin.TabularInline):
    model = UmbrellaProductBillOfMaterial
    extra = 0

class UmbrellaProductImageInline(DefaultInline):
    model = UmbrellaProductImage 

class ProductInline(DefaultInline):
    model=Product  
    extra=0
    # fields = ('name', 'umbrella_product_model',)  
    # exclude = ('description', 'complete', 'active')
    # readonly_fields = ('sku',)
    # can_delete = False 

class ProductBillOfMaterialInline(admin.TabularInline):
    model = ProductBillOfMaterial
    # readonly_fields = ['cost', 'availability'] #['materials_on_stock',]
    extra = 0    

#####################
### Custom Admins ###
#####################

class CollectionAdmin(admin.ModelAdmin):
    inlines = [UmbrellaProductInline]
    list_display = ['name', 'number','range_type', 'production_location']
    # readonly_fields = ()

class SizeAdmin(DefaultAdmin):
    inlines = [SizeBreedsInline]

class StockLocationAdmin(admin.ModelAdmin):
    inlines = [StockLocationItemInline]

class StockLocationItemAdmin(admin.ModelAdmin):
    list_display = ['material', 'quantity_in_stock', 'quantity_on_its_way', 'location']
    list_filter = ['location']
    search_fields = ['material']
    ordering = ('material', 'location')

class MaterialAdmin(DefaultAdmin):
    list_display = ['name', 'sku_supplier', 'supplier', 'cost_per_usage_unit', 'usage_units_on_stock']
    list_filter = ['supplier', 'mat_type']
    search_fields = ['name', 'supplier__business_name', 'sku_supplier', 'sku']
    readonly_fields = ['used_in_collections', 'used_in_products']
    inlines = [MaterialImageInline, MaterialDataSheetInline, StockLocationItemInline]

class UmbrellaProductModelAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'product_type', 'number', 'product_images_present']
    list_filter = ['product_type', 'number', 'product_images_present']
    inlines = [ProductModelInline, UmbrellaProductModelImageInline, UmbrellaProductModelProductionDescriptionInline]
    search_fields = ['name']
    # readonly_fields = ['used_in_collections']

class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'all_patterns_present', 'get_umbrella_poroduct_model_number']
    list_filter = ['all_patterns_present', 'umbrella_product_model__number']
    inlines = [ProductModelPatternInline]
    def get_umbrella_poroduct_model_number(self, obj):
        return obj.umbrella_product_model.number
    get_umbrella_poroduct_model_number.admin_order_field  = 'Model Number'  #Allows column order sorting
    get_umbrella_poroduct_model_number.short_description = 'Model Number'  #Renames column head


class UmbrellaProductAdmin(admin.ModelAdmin):
    # readonly_fields = ('sku', 'recommended_retail_price', 'recommended_B2B_price_per_1',
    #     'recommended_B2B_price_per_6', 'recommended_B2B_price_per_24',
    #     'recommended_B2B_price_per_96', 'cost', 'materials_on_stock',
    #     'materials_on_stock_in_production_location', 'materials_missing')    
    list_display = ['__unicode__','base_sku', 'active', 'complete', 'umbrella_product_model', 'number_of_sizes']
    list_filter = ['collection', 'colour', 'umbrella_product_model__product_type', 'complete', 'active']
    inlines = [ProductInline, UmbrellaProductBillOfMaterialInline, UmbrellaProductImageInline]
    # actions = [copy_product_action]

class UmbrellaProductBillOfMaterialAdmin(admin.ModelAdmin):
    readonly_fields = []

class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('sku', 'recommended_retail_price', 'recommended_B2B_price_per_1',
        'recommended_B2B_price_per_6', 'recommended_B2B_price_per_24',
        'recommended_B2B_price_per_96', 'cost', 'materials_on_stock',
        'materials_on_stock_in_production_location',)    
    list_display = ['name','sku', 'active', 'complete', 
        'materials_on_stock_in_production_location', 'recommended_retail_price', 
        'recommended_B2B_price_per_1', 'recommended_B2B_price_per_6', 
        'recommended_B2B_price_per_24', 'recommended_B2B_price_per_96',]  
    list_filter = ['umbrella_product__collection', 'umbrella_product__colour', 
        'umbrella_product__umbrella_product_model__product_type', 'product_model__size',  
        'product_model__umbrella_product_model__number', 'complete', 'active']
    inlines = [ProductBillOfMaterialInline]
    search_fields = ['sku',]

class ProductBillOfMaterialAdmin(admin.ModelAdmin):
    readonly_fields = []

admin.site.register(StockLocation, StockLocationAdmin)
admin.site.register(StockLocationMovement)
admin.site.register(Material, MaterialAdmin)
admin.site.register(MaterialDataSheet)
admin.site.register(MaterialImage)
admin.site.register(StockLocationItem, StockLocationItemAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Colour)
admin.site.register(ProductModel, ProductModelAdmin)
admin.site.register(ProductModelPattern)
admin.site.register(UmbrellaProductModel, UmbrellaProductModelAdmin)
admin.site.register(UmbrellaProductModelImage)
admin.site.register(UmbrellaProduct, UmbrellaProductAdmin)
admin.site.register(UmbrellaProductImage)
admin.site.register(UmbrellaProductBillOfMaterial, UmbrellaProductBillOfMaterialAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductBillOfMaterial, ProductBillOfMaterialAdmin)
