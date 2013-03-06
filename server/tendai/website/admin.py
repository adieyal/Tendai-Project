from django.contrib import admin
import models

class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'url', 'page', 'enabled')

class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'path')

class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'menu')
    
    def menu(self, object):
        menu_items = models.MenuItem.objects.filter(page=object)
        return ', '.join([m.__unicode__() for m in menu_items])

class StoryAdmin(admin.ModelAdmin):
    list_display = ('heading', 'monitor', 'country', 'submission_id', 'status')
    list_filter = ('status', 'country')
    exclude = ("submission", "photo")
    
    def submission_id(self, object):
        return object.submission.id

admin.site.register(models.MenuItem, MenuItemAdmin)
admin.site.register(models.Template, TemplateAdmin)
admin.site.register(models.Page, PageAdmin)
admin.site.register(models.Story, StoryAdmin)
