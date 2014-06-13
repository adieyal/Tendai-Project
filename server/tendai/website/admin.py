from django.contrib import admin
from django.http import HttpResponse, Http404
import models

class MenuItemAdmin(admin.ModelAdmin):
    def increase_order(self, request, queryset):
        """
        Move selected items up.
        """
        for item in queryset:
            if item.order > 0:
                item.order = item.order - 1
                item.save()

    increase_order.short_description = "Push menu items up"

    def decrease_order(self, request, queryset):
        """
        Move selected items up.
        """
        for item in queryset:
            item.order = item.order + 1
            item.save()

    decrease_order.short_description = "Push menu items down"
    actions = ['decrease_order', 'increase_order']

    list_display = ('__unicode__', 'url', 'page', 'enabled', 'order')

class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'path')

class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'menu')
    
    def menu(self, object):
        menu_items = models.MenuItem.objects.filter(page=object)
        return ', '.join([m.__unicode__() for m in menu_items])

class StoryAdmin(admin.ModelAdmin):
    list_display = ('heading', 'monitor', 'country', 'submission_id', 'status', 'date')
    list_filter = ('status', 'country', 'submission__end_time')
    exclude = ("submission", "photo")

    
    def date(self, obj):
        return obj.submission.end_time

    def submission_id(self, object):
        return object.submission.id
    date.admin_order_field = 'submission__end_time'

admin.site.register(models.MenuItem, MenuItemAdmin)
admin.site.register(models.Template, TemplateAdmin)
admin.site.register(models.Page, PageAdmin)
admin.site.register(models.Story, StoryAdmin)
