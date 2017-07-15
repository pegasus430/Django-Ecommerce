from django.contrib import admin

from .models import Relation

class RelationAdmin(admin.ModelAdmin):
	list_display = ('business_name', 'contact_phone')

admin.site.register(Relation, RelationAdmin)