from django.contrib import admin
import models

class MOHInteractionLevelAdmin(admin.ModelAdmin):
    list_display = ('level', 'country', 'created',)
    list_filter = ('country',)

class ProjectCostAdmin(admin.ModelAdmin):
    list_display = ('cost', 'country', 'created',)
    list_filter = ('country',)

admin.site.register(models.MOHInteractionLevel, MOHInteractionLevelAdmin)
admin.site.register(models.ProjectCost, ProjectCostAdmin)
