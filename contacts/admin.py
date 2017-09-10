from django.contrib import admin

from .models import Relation, RelationAddress, OwnAddress, Agent

class RelationAdmin(admin.ModelAdmin):
	list_display = ('business_name', 'contact_name', 'contact_phone')
	list_filter = ['is_supplier', 'is_client', 'country', 'agent']


class OwnAddressAdmin(admin.ModelAdmin):
	pass

admin.site.register(Agent)
admin.site.register(Relation, RelationAdmin)
admin.site.register(OwnAddress, OwnAddressAdmin)
admin.site.register(RelationAddress)