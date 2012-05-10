from django.contrib import admin
import models

class MOHInteractionLevelAdmin(admin.ModelAdmin):
    list_display = ('level', 'country', 'date',)
    list_filter = ('country',)

class DisbursementAdmin(admin.ModelAdmin):
    list_display = ('amount', 'country', 'date',)
    list_filter = ('country',)

admin.site.register(models.MOHInteractionLevel, MOHInteractionLevelAdmin)
admin.site.register(models.Disbursement, DisbursementAdmin)
