from django.contrib import admin
from defaults.admin import DefaultAdmin, DefaultInline

from .models import *

###############
### Inlines ###
###############
class ProductionOrderItemInline(DefaultInline):
	model = ProductionOrderItem

#####################
### Custom Admins ###
#####################
class ProductionOrderAdmin(DefaultAdmin):
	inlines = [ProductionOrderItemInline]
	readonly_fields = ['missing_materials']
	list_display = ['__unicode__', 'status']

class ProductionOrderItemAdmin(DefaultAdmin):
	pass


admin.site.register(ProductionOrder, ProductionOrderAdmin)
admin.site.register(ProductionOrderItem, ProductionOrderItemAdmin)