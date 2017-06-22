from django.contrib import admin


def copy_object(modeladmin, request, queryset):
    for obj in queryset:
        new_obj = obj
        new_obj.pk = None
        try:
        	new_obj.name += ' (Copy)'
        except AttributeError:
        	pass
        new_obj.save()
copy_object.short_description = "Copy Object"


class DefaultAdmin(admin.ModelAdmin):
    actions = [copy_object]