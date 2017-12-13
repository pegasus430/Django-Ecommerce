from django.contrib import admin
from defaults.admin import DefaultAdmin

from .models import LabelLogo

class LabelLogoAdmin(admin.ModelAdmin):
    pass

admin.site.register(LabelLogo, LabelLogoAdmin)