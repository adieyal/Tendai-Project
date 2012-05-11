from django.contrib import admin
import models

class MOHInteractionLevelAdmin(admin.ModelAdmin):
    list_display = ('country', 'date', 'level',)
    list_filter = ('country',)

class MOHInteractionAdmin(admin.ModelAdmin):
    list_display = ('country', 'date', 'type',)
    list_filter = ('country',)

class MOHInteractionTypeAdmin(admin.ModelAdmin):
    list_display = ('country', 'date', 'type',)
    list_filter = ('country',)

class DisbursementAdmin(admin.ModelAdmin):
    list_display = ('country', 'date', 'amount',)
    list_filter = ('country',)

class TendaiProgressReportAdmin(admin.ModelAdmin):
    list_display = ('country', 'date', 'reporting', 'adjustment')
    list_filter = ('country',)
    fieldsets = (
        ('General', {
                'fields': ('country', 'date')
                }),
        ('Grantee reporting satisfactory?', {
                'fields': ('reporting', 'reporting_comment')
                }),
        ('Grantee adjusting according to recommendations?', {
                'fields': ('adjustment', 'adjustment_comment')
                })
        )

class RiskAdmin(admin.ModelAdmin):
    list_display = ('country', 'date', 'level', 'comment')
    list_filter = ('country', 'level')
    


admin.site.register(models.MOHInteractionLevel, MOHInteractionLevelAdmin)
admin.site.register(models.MOHInteractionType)#, MOHInteractionAdmin)
admin.site.register(models.MOHInteraction, MOHInteractionAdmin)
admin.site.register(models.Disbursement, DisbursementAdmin)
admin.site.register(models.TendaiProgressReport, TendaiProgressReportAdmin)
admin.site.register(models.Risk, RiskAdmin)
