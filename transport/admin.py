from django.contrib import admin
from defaults.admin import DefaultAdmin, DefaultInline


from .models import *
from .helpers import print_picking_list, print_stock_label_38x90

###############
### Inlines ###
###############
class InternalTransportMaterialInline(DefaultInline):
	model = InternalTransportMaterial


##############
### Admins ###
##############
class InternalTransportAdmin(DefaultAdmin):
    list_display = ['__unicode__', 'status']
    inlines = [InternalTransportMaterialInline]
    actions = [print_picking_list, print_stock_label_38x90]

class InternalTransportMaterialAdmin(DefaultAdmin):
	pass

admin.site.register(InternalTransport, InternalTransportAdmin)
admin.site.register(InternalTransportMaterial, InternalTransportMaterialAdmin)
