from django.contrib import admin
import models

class MedicineStockAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'facility', 'timestamp', 'amount', 'inconsistent')
    list_filter = ('medicine', 'facility')

class MedicineRestockExpectationAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'facility', 'timestamp', 'start', 'end', 'amount', 'inconsistent')
    list_filter = ('medicine', 'facility')

class MedicineRestockAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'facility', 'timestamp', 'start', 'end', 'amount', 'inconsistent')
    list_filter = ('medicine', 'facility')

class MedicineStockoutAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'facility', 'submission_id', 'country')
    list_filter = ('medicine', 'facility', 'submission__end_time', 'submission__submissionworkerdevice__community_worker__country')
    exclude = ('submission',)

    def submission_id(self, object):
        return object.submission.id

    def country(self, object):
        return object.submission.submissionworkerdevice.community_worker.country

admin.site.register(models.MedicineStock, MedicineStockAdmin)
admin.site.register(models.MedicineRestockExpectation, MedicineRestockExpectationAdmin)
admin.site.register(models.MedicineRestock, MedicineRestockAdmin)
admin.site.register(models.MedicineStockout, MedicineStockoutAdmin)
