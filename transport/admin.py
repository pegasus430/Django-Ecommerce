from django.contrib import admin
from defaults.admin import DefaultAdmin, DefaultInline


from .models import *

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

class InternalTransportMaterialAdmin(DefaultAdmin):
	pass

admin.site.register(InternalTransport, InternalTransportAdmin)
admin.site.register(InternalTransportMaterial, InternalTransportMaterialAdmin)
