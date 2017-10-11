from copy import deepcopy

from django.contrib import admin

def copy_object(obj):
    new_obj = deepcopy(obj)
    new_obj.pk = None
    try:
        new_obj.name += ' (Copy)'
    except AttributeError:
        pass
    new_obj.save()

def copy_object_action(modeladmin, request, queryset):
    for obj in queryset:
        copy_object(obj)
copy_object_action.short_description = "Copy Object"


class DefaultAdmin(admin.ModelAdmin):
    actions = [copy_object_action]
    pass

class DefaultInline(admin.TabularInline):
    extra = 0
    classes = ['collapse']

class DefaultExpandedInline(admin.TabularInline):
    extra = 0
    # classes = ['collapse']    