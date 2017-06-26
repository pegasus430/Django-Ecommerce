from django.contrib import admin

from .models import Supplier

class SupplierAdmin(admin.ModelAdmin):
	list_display = ('business_name', 'contact_phone')

admin.site.register(Supplier, SupplierAdmin)