from django.contrib import admin
from defaults.admin import DefaultInline, DefaultAdmin

from .models import Relation, RelationAddress, OwnAddress, Agent, AgentCommission
from .helpers import print_address_label #, print_commisson_report

### Inlines ###

class AgentCommissionInline(DefaultInline):
    model = AgentCommission

### Admins ###

class AgentAdmin(DefaultAdmin):
    inlines = [AgentCommissionInline]
    # actions = [print_commisson_report]

class AgentCommissionAdmin(DefaultAdmin):
    pass

class RelationAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'contact_name', 'contact_phone')
    list_filter = ['is_supplier', 'is_client', 'country', 'agent']
    actions = [print_address_label]

class OwnAddressAdmin(admin.ModelAdmin):
    actions = [print_address_label]

admin.site.register(Agent, AgentAdmin)
admin.site.register(AgentCommission, AgentCommissionAdmin)
admin.site.register(Relation, RelationAdmin)
admin.site.register(OwnAddress, OwnAddressAdmin)
admin.site.register(RelationAddress)