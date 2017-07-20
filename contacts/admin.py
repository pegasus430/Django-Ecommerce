from django.contrib import admin

from .models import Relation, OwnAddress

class RelationAdmin(admin.ModelAdmin):
	list_display = ('business_name', 'contact_name', 'contact_phone')


class OwnAddressAdmin(admin.ModelAdmin):
	pass

admin.site.register(Relation, RelationAdmin)
admin.site.register(OwnAddress, OwnAddressAdmin)